# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

OLD_MODULE = "oxigen_l10n_es"
NEW_MODULE = "l10n_es_extension"

# Complete list of the records this version hands over to
# l10n_es_extension. The terminal xml-id names are identical in both
# modules by design; the name overrides of the official l10n_es
# templates move with the data files alone (they carry no xml-id of
# this module), so they need no entry here.
MOVED = {
    "account.tax.template": [
        "account_tax_template_p_iva4_nd_bc",
        "account_tax_template_p_iva4_nd_bi",
        "account_tax_template_p_iva10_nd_bc",
        "account_tax_template_p_iva10_nd_bi",
        "account_tax_template_p_iva0_nd_bc",
        "account_tax_template_p_iva0_nd_bi",
        "account_tax_template_p_iva4nd_ic_bc",
        "account_tax_template_p_iva4nd_ic_bi",
        "account_tax_template_p_iva4nd_sp_in",
        "account_tax_template_p_iva10nd_ic_bc",
        "account_tax_template_p_iva10nd_ic_bi",
        "account_tax_template_p_iva10nd_sp_in",
        "account_tax_template_p_iva21nd_ic_bc",
        "account_tax_template_p_iva21nd_ic_bi",
        "account_tax_template_p_iva21nd_sp_in",
    ],
    "account.fiscal.position.tax.template": [
        "fptt_intra_nd4s",
        "fptt_intra_nd10s",
        "fptt_intra_nd21s",
        "fptt_intra_nd4b",
        "fptt_intra_nd10b",
        "fptt_intra_nd21b",
        "fptt_intra_nd4_inv",
        "fptt_intra_nd10_inv",
        "fptt_intra_nd21b_inv",
        "fptt_irpf15_nd4_nd4",
        "fptt_irpf15_nd10_nd10",
        "fptt_irpf15_nd21_nd21",
        "fptt_irpf15_nd4_irpf15",
        "fptt_irpf15_nd10_irpf15",
        "fptt_irpf15_nd21_irpf15",
    ],
}
# Company-plane model instantiated from each template model (the chart
# wizard stamps those records as <module>.<company_id>_<template_name>).
COMPANY_MODEL = {
    "account.tax.template": "account.tax",
    "account.fiscal.position.tax.template": "account.fiscal.position.tax",
}


def _rep_sig(lines):
    # Template repartition lines carry no sequence field (only the real
    # ones do); sort by the ordering key the model actually has.
    key = "sequence" if "sequence" in lines._fields else "id"
    return [
        (
            line.repartition_type,
            line.factor_percent,
            line.account_id.id,
            tuple(sorted(line.tag_ids.ids)),
        )
        for line in lines.sorted(key)
    ]


def _same_shape(model, old, new):
    """Is the record the extension just declared identical to ours?

    Field-level guard against copy drift between the two modules'
    data files: a mismatch means the declarations diverged and the
    handover must not silently pick one side.
    """
    if model == "account.tax.template":
        return (
            old.name == new.name
            and old.amount_type == new.amount_type
            and old.amount == new.amount
            and old.type_tax_use == new.type_tax_use
            and old.price_include == new.price_include
            and old.analytic == new.analytic
            and old.tax_group_id == new.tax_group_id
            and old.chart_template_id == new.chart_template_id
            and _rep_sig(old.invoice_repartition_line_ids)
            == _rep_sig(new.invoice_repartition_line_ids)
            and _rep_sig(old.refund_repartition_line_ids)
            == _rep_sig(new.refund_repartition_line_ids)
        )
    return (
        old.position_id == new.position_id
        and old.tax_src_id == new.tax_src_id
        and old.tax_dest_id == new.tax_dest_id
    )


def _drop_owned_children(record):
    """Delete the one2many children of the duplicate before repointing.

    The children (e.g. repartition line templates) are components of
    the duplicate, not references to it: they must die with it, never
    be adopted by the record we keep.
    """
    for field in record._fields.values():
        if field.type == "one2many" and field.inverse_name:
            record[field.name].unlink()


def _repoint(env, model, new_id, old_id):
    """Move every stored reference from the duplicate to the kept record.

    Discovered dynamically from the registry, no table of any module
    is named (same doctrine as the 14.0.1.0.9 dedup): every stored
    many2one and many2many whose comodel is ``model`` is rewritten
    from ``new_id`` to ``old_id``; one2many storage is the inverse
    many2one, so it is covered. many2many rows are deduplicated
    against an existing link to the kept record before the move.
    """
    cr = env.cr
    seen_m2m = set()
    for model_name in env.registry:
        m = env[model_name]
        if m._abstract or m._transient or not m._auto:
            continue
        for field in m._fields.values():
            if not field.store or field.comodel_name != model:
                continue
            if field.type == "many2one":
                cr.execute(
                    'UPDATE "{}" SET "{}" = %s WHERE "{}" = %s'.format(
                        m._table, field.name, field.name
                    ),
                    (old_id, new_id),
                )
            elif field.type == "many2many":
                key = (field.relation, field.column2)
                if key in seen_m2m:
                    continue
                seen_m2m.add(key)
                rel, col1, col2 = field.relation, field.column1, field.column2
                cr.execute(
                    'UPDATE "{r}" SET "{c2}" = %s WHERE "{c2}" = %s'
                    ' AND NOT EXISTS (SELECT 1 FROM "{r}" x'
                    ' WHERE x."{c1}" = "{r}"."{c1}" AND x."{c2}" = %s)'.format(
                        r=rel, c1=col1, c2=col2
                    ),
                    (old_id, new_id, old_id),
                )
                cr.execute(
                    'DELETE FROM "{r}" WHERE "{c2}" = %s'.format(r=rel, c2=col2),
                    (new_id,),
                )


def migrate(cr, version):
    """Hand the non-deductible family over to l10n_es_extension.

    l10n_es_extension (a new dependency, so it always loads first)
    now declares the same templates under the same terminal names, so
    on an existing database this update leaves two records per key:
    OURS (the historical one, wired to maps, positions and company
    taxes) and the extension's fresh duplicate. Per key:

    - keep OUR record: repoint every reference from the duplicate to
      it, delete the duplicate, point the extension's xml-id at it and
      drop ours — the record itself is never touched;
    - company plane: records born from our templates just change
      custody (xml-id module switch), nothing else — the wizard is the
      only thing that ever duplicates per company, and it did not run.

    On a fresh install this script never runs and the extension's
    declarations are the only ones. Idempotent: a key already handed
    over is skipped.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    imd_model = env["ir.model.data"]
    for model, names in MOVED.items():
        for name in names:
            old_imd = imd_model.search(
                [
                    ("module", "=", OLD_MODULE),
                    ("model", "=", model),
                    ("name", "=", name),
                ]
            )
            new_imd = imd_model.search(
                [
                    ("module", "=", NEW_MODULE),
                    ("model", "=", model),
                    ("name", "=", name),
                ]
            )
            if not old_imd:
                continue  # nothing to hand over (fresh DB or already done)
            if not new_imd:
                raise RuntimeError(
                    "ND handover: %s.%s (%s) has no counterpart under %s;"
                    " update both modules together"
                    % (OLD_MODULE, name, model, NEW_MODULE)
                )
            old = env[model].browse(old_imd.res_id).exists()
            new = env[model].browse(new_imd.res_id).exists()
            if not old:
                old_imd.unlink()
                continue
            if not new or old.id == new.id:
                raise RuntimeError(
                    "ND handover: inconsistent records for %s (%s): old=%s new=%s"
                    % (name, model, old_imd.res_id, new_imd.res_id)
                )
            if not _same_shape(model, old, new):
                raise RuntimeError(
                    "ND handover: %s (%s) diverges between %s and %s;"
                    " refusing to merge different definitions"
                    % (name, model, OLD_MODULE, NEW_MODULE)
                )
            _drop_owned_children(new)
            _repoint(env, model, new.id, old.id)
            env.cache.invalidate()
            # Repoint the extension's xml-id BEFORE deleting the duplicate:
            # unlink() garbage-collects every ir.model.data row still
            # pointing at the deleted record, so the reversed order killed
            # the key silently and every later cross-module reference to
            # it crashed the update.
            new_imd.write({"res_id": old.id})
            old_imd.unlink()
            new.unlink()
            resolved = env.ref("%s.%s" % (NEW_MODULE, name), raise_if_not_found=False)
            if not resolved or resolved.id != old.id:
                raise RuntimeError(
                    "ND handover: %s.%s does not resolve to the kept record"
                    " %s after the swap (got %s)"
                    % (NEW_MODULE, name, old.id, resolved and resolved.id)
                )
            _logger.info(
                "ND handover: %s (%s) kept as record %s under %s",
                name,
                model,
                old.id,
                NEW_MODULE,
            )

    # Company plane: custody switch of the wizard-instantiated records.
    for model, names in MOVED.items():
        company_model = COMPANY_MODEL[model]
        pattern = r"^\d+_(%s)$" % "|".join(names)
        cr.execute(
            """
            SELECT o.id, o.name
              FROM ir_model_data o
              JOIN ir_model_data n
                ON n.name = o.name AND n.model = o.model AND n.module = %s
             WHERE o.module = %s AND o.model = %s AND o.name ~ %s
            """,
            (NEW_MODULE, OLD_MODULE, company_model, pattern),
        )
        clashes = cr.fetchall()
        if clashes:
            raise RuntimeError(
                "ND handover: %s already owns company records %s"
                % (NEW_MODULE, [c[1] for c in clashes])
            )
        cr.execute(
            """
            UPDATE ir_model_data
               SET module = %s
             WHERE module = %s AND model = %s AND name ~ %s
            """,
            (NEW_MODULE, OLD_MODULE, company_model, pattern),
        )
        _logger.info(
            "ND handover: %s %s company records rebadged to %s",
            cr.rowcount,
            company_model,
            NEW_MODULE,
        )
