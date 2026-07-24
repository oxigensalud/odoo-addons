# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
"""Prune the obsolete E-family taxes for good, keeping posted history.

ForgeFlow created in 2022 a family of obsolete "(1)/(2)" reverse-charge /
intracommunity legs (``p_iva{4,10,21}_{sp_in,ic_bc,ic_bi,sp_ex,isp}_{1,2}``)
as ``oxigen_l10n_es`` records, modelling the v11 way (children of a group
tax) instead of using the single-tax taxes core ``l10n_es`` already ships
un-suffixed (``p_iva{4,10,21}_{sp_in,ic_bc,ic_bi,sp_ex,isp}``). On a database
installed from those data files there are, per key, several populations:

- the official ``l10n_es`` corpses: archived long ago, never used, merely
  SQUATTING company-plane xml-ids, with only group-era filiation debris left;
- OUR ``oxigen_l10n_es`` instances: a handful carry posted history that stays
  no matter what;
- OUR ``oxigen_l10n_es`` templates: the obsolete blueprints.

This migration removes the duplication for good:

1. delete the corpses (archived + never used + gates re-checked at run time)
   so the original names are freed;
2. archive our instances and set ``noupdate=true`` on their xml-ids -- they
   KEEP the posted history and their ``oxigen`` identity, and ride the
   end-of-update orphan sweep untouched;
3. delete the obsolete templates -- the data files no longer declare them
   (poda) and the AEAT maps have been requalified to the un-suffixed core
   originals, so nothing references or re-creates them.

Our instances are ARCHIVED, not deleted, on purpose: posted account moves
reference them, so the records must survive. Only the unreferenced corpses and
the history-less templates are deleted. The group-era filiation of a deleted
corpse is REPOINTED to our surviving (archived) twin, never dropped.

Because the data files no longer declare the E-family, updating the module
again is innocuous: nothing re-creates the templates and ``noupdate`` keeps
the archived instances. On a fresh install this script never runs
(``if not version``); an already-pruned database (no corpses, no obsolete
templates, our instances archived) is detected and skipped.

The gate that guards the corpse deletion discovers every inbound reference
through registry introspection -- the framework enumerates the tables, this
module names none.
"""
import logging
import re

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

CORE_MODULE = "l10n_es"
OXIGEN_MODULE = "oxigen_l10n_es"
TAX_MODEL = "account.tax"
TEMPLATE_MODEL = "account.tax.template"
# Company-plane instances carry the "<company_id>_" xml-id prefix; templates
# do not.
INSTANCE_RE = (
    r"^[0-9]+_account_tax_template_p_iva(4|10|21)"
    r"_(sp_in|ic_bc|ic_bi|sp_ex|isp)_(1|2)$"
)
TEMPLATE_RE = (
    r"^account_tax_template_p_iva(4|10|21)_(sp_in|ic_bc|ic_bi|sp_ex|isp)_(1|2)$"
)
# The core self-relation that stores group-tax filiation (children_tax_ids):
# debris here, repointed, never treated as a blocking reference.
FILIATION_TABLE = "account_tax_filiation_rel"
REF_RE = r"^account\.tax,[0-9]+$"


def _ids_by_module(cr, module):
    """Company-plane E tax ids whose xml-id currently lives under ``module``."""
    cr.execute(
        """
        SELECT t.id
          FROM ir_model_data d
          JOIN account_tax t ON t.id = d.res_id
         WHERE d.model = 'account.tax' AND d.module = %s AND d.name ~ %s
        """,
        (module, INSTANCE_RE),
    )
    return [row[0] for row in cr.fetchall()]


def _template_ids(cr):
    """Obsolete E-family ``account.tax.template`` ids under our namespace."""
    cr.execute(
        """
        SELECT t.id
          FROM ir_model_data d
          JOIN account_tax_template t ON t.id = d.res_id
         WHERE d.model = 'account.tax.template' AND d.module = %s AND d.name ~ %s
        """,
        (OXIGEN_MODULE, TEMPLATE_RE),
    )
    return [row[0] for row in cr.fetchall()]


def _any_active(cr, ids):
    """Count of ``ids`` that are still active."""
    cr.execute("SELECT count(*) FROM account_tax WHERE id = ANY(%s) AND active", (ids,))
    return cr.fetchone()[0]


def _component_columns(env, model):
    """(table, column) pairs that store the model's own one2many children."""
    cols = set()
    for field in env[model]._fields.values():
        if field.type == "one2many" and field.inverse_name:
            comodel = env[field.comodel_name]
            if comodel._auto and not comodel._abstract and not comodel._transient:
                cols.add((comodel._table, field.inverse_name))
    return cols


def _blocking_refs(env, ids):
    """Registry-discovered inbound references to ``ids`` that block deletion.

    Every stored many2one / many2many whose comodel is account.tax, every
    stored fields.Reference column, and the ir.property reference channel are
    swept -- no foreign table is ever named (closure doctrine). The tax's own
    repartition components (one2many) and the group-filiation self-relation
    are excluded: the former die with the record, the latter is repointed.
    Returns a list of "channel: count" strings (empty when nothing references
    ``ids``).
    """
    cr = env.cr
    excluded = _component_columns(env, TAX_MODEL)
    details = []
    seen_m2m = set()
    for model_name in env.registry:
        model = env[model_name]
        if model._abstract or model._transient or not model._auto:
            continue
        for field in model._fields.values():
            if not field.store:
                continue
            if field.comodel_name == TAX_MODEL and field.type == "many2one":
                if (model._table, field.name) in excluded:
                    continue
                sql = 'SELECT count(*) FROM "{}" WHERE "{}" = ANY(%s)'.format(
                    model._table, field.name
                )
                cr.execute(sql, (ids,))
            elif field.comodel_name == TAX_MODEL and field.type == "many2many":
                if field.relation == FILIATION_TABLE:
                    continue
                key = (field.relation, field.column2)
                if key in seen_m2m:
                    continue
                seen_m2m.add(key)
                sql = 'SELECT count(*) FROM "{}" WHERE "{}" = ANY(%s)'.format(
                    field.relation, field.column2
                )
                cr.execute(sql, (ids,))
            elif field.type == "reference":
                sql = (
                    'SELECT count(*) FROM "{t}" WHERE "{c}" ~ %s '
                    "AND split_part(\"{c}\", ',', 2)::int = ANY(%s)"
                ).format(t=model._table, c=field.name)
                cr.execute(sql, (REF_RE, ids))
            else:
                continue
            count = cr.fetchone()[0]
            if count:
                details.append("%s.%s: %s" % (model_name, field.name, count))
    cr.execute(
        "SELECT count(*) FROM ir_property WHERE value_reference ~ %s"
        " AND split_part(value_reference, ',', 2)::int = ANY(%s)",
        (REF_RE, ids),
    )
    count = cr.fetchone()[0]
    if count:
        details.append("ir.property: %s" % count)
    return details


def _ir_default_refs(cr, ids):
    """ir_default JSON defaults embedding any of ``ids``."""
    cr.execute(
        "SELECT d.id, d.json_value FROM ir_default d"
        " JOIN ir_model_fields f ON f.id = d.field_id"
        " WHERE f.relation = 'account.tax'"
    )
    rows = cr.fetchall()
    if not rows:
        return []
    pattern = re.compile(r"(^|[^0-9])(%s)([^0-9]|$)" % "|".join(str(i) for i in ids))
    return ["ir_default %s" % did for did, jv in rows if jv and pattern.search(jv)]


def _assert_no_living_group(cr, ids):
    """No living group tax may still aggregate an E child."""
    cr.execute(
        """
        SELECT count(DISTINCT f.parent_tax)
          FROM account_tax_filiation_rel f
          JOIN account_tax p ON p.id = f.parent_tax AND p.amount_type = 'group'
         WHERE f.child_tax = ANY(%s)
        """,
        (ids,),
    )
    living = cr.fetchone()[0]
    if living:
        raise RuntimeError(
            "E-family poda: %s living group taxes still use E children -"
            " filiation is not debris here" % living
        )


def _assert_deletable(env, a_ids):
    """Corpse-deletion safety checks: inactive and unreferenced."""
    cr = env.cr
    # Every deletion target must be INACTIVE (archived long ago; an active one
    # means the world changed -> human eyes first).
    cr.execute(
        "SELECT count(*) FROM account_tax WHERE id = ANY(%s) AND active",
        (a_ids,),
    )
    active = cr.fetchone()[0]
    if active:
        raise RuntimeError(
            "E-family poda: %s l10n_es corpses are ACTIVE - refusing to"
            " delete" % active
        )
    # No reference outside the tax's own composition and the filiation debris
    # may point at a deletion target (registry sweep + ir_default).
    details = _blocking_refs(env, a_ids) + _ir_default_refs(cr, a_ids)
    if details:
        raise RuntimeError(
            "E-family poda: deletion targets still referenced (%s)" % "; ".join(details)
        )


def _repoint_filiation(cr, a_ids):
    """Repoint every parent->corpse filiation row to the adopted child.

    Never deleted: the parent (a living official tax) keeps aggregating the
    child it should have -- now the adopted record instead of the corpse.
    """
    # Pre-check every row repoints cleanly (twin exists, no collision on the
    # parent, no tax-use clash).
    cr.execute(
        """
        SELECT count(*)
          FROM account_tax_filiation_rel f
          JOIN ir_model_data dc ON dc.model = 'account.tax'
                               AND dc.module = %s AND dc.res_id = f.child_tax
                               AND dc.name ~ %s
          LEFT JOIN ir_model_data do2 ON do2.model = 'account.tax'
                                     AND do2.module = %s AND do2.name = dc.name
         WHERE do2.res_id IS NULL
            OR EXISTS (SELECT 1 FROM account_tax_filiation_rel f2
                        WHERE f2.parent_tax = f.parent_tax
                          AND f2.child_tax = do2.res_id)
            OR EXISTS (SELECT 1 FROM account_tax p, account_tax c2
                        WHERE p.id = f.parent_tax AND c2.id = do2.res_id
                          AND c2.type_tax_use <> 'none'
                          AND p.type_tax_use <> c2.type_tax_use)
        """,
        (CORE_MODULE, INSTANCE_RE, OXIGEN_MODULE),
    )
    bad = cr.fetchone()[0]
    if bad:
        raise RuntimeError(
            "E-family poda: %s filiation rows cannot be repointed cleanly"
            " (missing twin / collision / type clash)" % bad
        )
    cr.execute(
        """
        UPDATE account_tax_filiation_rel f
           SET child_tax = do2.res_id
          FROM ir_model_data dc, ir_model_data do2
         WHERE dc.model = 'account.tax' AND dc.module = %s
           AND dc.res_id = f.child_tax AND dc.name ~ %s
           AND do2.model = 'account.tax' AND do2.module = %s
           AND do2.name = dc.name
        """,
        (CORE_MODULE, INSTANCE_RE, OXIGEN_MODULE),
    )
    n_rep = cr.rowcount
    cr.execute(
        "SELECT count(*) FROM account_tax_filiation_rel WHERE child_tax = ANY(%s)",
        (a_ids,),
    )
    left = cr.fetchone()[0]
    if left:
        raise RuntimeError(
            "E-family poda: %s filiation rows still point at corpses after"
            " repoint" % left
        )
    return n_rep


def _delete_corpses(cr, a_ids):
    """Delete the corpses, composition -> identity -> record.

    The xml-id delete also drops squatter l10n_es E keys with no live tax, so
    the original name is truly freed.
    """
    cr.execute(
        """
        DELETE FROM account_account_tag_account_tax_repartition_line_rel
         WHERE account_tax_repartition_line_id IN (
               SELECT id FROM account_tax_repartition_line
                WHERE invoice_tax_id = ANY(%s) OR refund_tax_id = ANY(%s))
        """,
        (a_ids, a_ids),
    )
    cr.execute(
        "DELETE FROM account_tax_repartition_line"
        " WHERE invoice_tax_id = ANY(%s) OR refund_tax_id = ANY(%s)",
        (a_ids, a_ids),
    )
    cr.execute(
        "DELETE FROM mail_followers WHERE res_model = 'account.tax'"
        " AND res_id = ANY(%s)",
        (a_ids,),
    )
    cr.execute(
        "DELETE FROM mail_message WHERE model = 'account.tax'" " AND res_id = ANY(%s)",
        (a_ids,),
    )
    cr.execute(
        "DELETE FROM ir_translation WHERE name LIKE %s AND res_id = ANY(%s)",
        ("account.tax,%", a_ids),
    )
    cr.execute(
        "DELETE FROM ir_model_data WHERE model = 'account.tax'" " AND res_id = ANY(%s)",
        (a_ids,),
    )
    cr.execute(
        "DELETE FROM ir_model_data WHERE model = 'account.tax'"
        " AND module = %s AND name ~ %s",
        (CORE_MODULE, INSTANCE_RE),
    )
    cr.execute("DELETE FROM account_tax WHERE id = ANY(%s)", (a_ids,))
    return cr.rowcount


def _archive_instances(cr, b_ids):
    """Archive our E instances and protect them from the orphan sweep.

    KEPT under ``oxigen_l10n_es`` (no re-badge): the data-file poda means
    nothing re-creates them, and ``noupdate=true`` stops the end-of-update
    orphan cleanup from deleting them. They carry posted history and keep the
    OBSOLETE name -- they ARE obsolete. Returns ``(n_protected, n_archived)``.
    """
    cr.execute(
        "UPDATE ir_model_data SET noupdate = true"
        " WHERE model = 'account.tax' AND module = %s AND name ~ %s",
        (OXIGEN_MODULE, INSTANCE_RE),
    )
    n_protect = cr.rowcount
    cr.execute(
        "UPDATE account_tax SET active = false WHERE id = ANY(%s) AND active",
        (b_ids,),
    )
    return n_protect, cr.rowcount


def _delete_templates(env, tpl_ids):
    """Delete the obsolete E-family templates through the ORM.

    Templates carry no posted history and are not mail-tracked, so the ORM
    unlink is the clean choice: it cascades every dependent (template
    repartition lines, template filiation, the AEAT-map m2m links, xml-ids,
    translations) that raw SQL would otherwise have to name one by one. After
    the map requalify + the legacy poda nothing references or re-declares them.
    """
    if not tpl_ids:
        return 0
    env[TEMPLATE_MODEL].browse(tpl_ids).unlink()
    return len(tpl_ids)


def _assert_post_state(cr, b_ids):
    """Post-checks: corpses gone, instances archived+protected, templates gone."""
    # No l10n_es corpse left under the E-family xml-ids.
    cr.execute(
        "SELECT count(*) FROM ir_model_data"
        " WHERE model = 'account.tax' AND module = %s AND name ~ %s",
        (CORE_MODULE, INSTANCE_RE),
    )
    if cr.fetchone()[0]:
        raise RuntimeError("E-family poda: l10n_es corpses survived the deletion")
    # Our instances: all archived, and every xml-id protected with noupdate.
    if _any_active(cr, b_ids):
        raise RuntimeError("E-family poda: our E instances still active after archive")
    cr.execute(
        "SELECT count(*) FROM ir_model_data"
        " WHERE model = 'account.tax' AND module = %s AND name ~ %s"
        " AND NOT noupdate",
        (OXIGEN_MODULE, INSTANCE_RE),
    )
    if cr.fetchone()[0]:
        raise RuntimeError("E-family poda: some instance xml-ids left unprotected")
    # No E-family template left anywhere (deleted, not re-badged).
    cr.execute(
        "SELECT count(*) FROM ir_model_data"
        " WHERE model = 'account.tax.template' AND name ~ %s",
        (TEMPLATE_RE,),
    )
    if cr.fetchone()[0]:
        raise RuntimeError("E-family poda: obsolete templates survived the deletion")


def migrate(cr, version):
    """Delete the E-family corpses + templates and archive our instances."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})

    a_ids = _ids_by_module(cr, CORE_MODULE)  # corpses -> DELETE
    b_ids = _ids_by_module(cr, OXIGEN_MODULE)  # our instances -> ARCHIVE (keep)
    tpl_ids = _template_ids(cr)  # obsolete templates -> DELETE

    # Anti silent no-op + idempotency: after a successful pass the corpses and
    # the templates are gone and our instances remain (archived). Detect the
    # already-pruned state and skip; refuse to no-op on an unexpected shape.
    if not a_ids and not tpl_ids:
        if b_ids and not _any_active(cr, b_ids):
            _logger.info("E-family poda: already applied, skipping")
            return
        raise RuntimeError(
            "E-family poda: no corpses and no obsolete templates, but instance"
            " state is unexpected (%s instances, %s active) - refusing to"
            " no-op silently" % (len(b_ids), _any_active(cr, b_ids))
        )

    _assert_no_living_group(cr, a_ids + b_ids)

    n_rep = n_del = 0
    if a_ids:
        _assert_deletable(env, a_ids)
        n_rep = _repoint_filiation(cr, a_ids)
        n_del = _delete_corpses(cr, a_ids)

    n_protect, n_arch = _archive_instances(cr, b_ids)
    n_tpl = _delete_templates(env, tpl_ids)
    _assert_post_state(cr, b_ids)

    _logger.info(
        "E-family poda OK: %s corpses deleted - %s instances archived+protected"
        " (%s xml-ids noupdate, %s total kept under oxigen) - %s obsolete"
        " templates deleted - %s filiation rows repointed",
        n_del,
        n_arch,
        n_protect,
        len(b_ids),
        n_tpl,
        n_rep,
    )
