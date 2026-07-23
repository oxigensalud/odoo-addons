# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

TEMPLATE_KEY = "account_tax_template_p_iva5_nd"


def _same_shape(tax, template):
    """Is the tax functionally identical to the official template?"""

    def sig(lines):
        # Template repartition lines carry no sequence field (only the
        # real ones do); each side sorts by the ordering key it has.
        key = "sequence" if "sequence" in lines._fields else "id"
        return [
            (line.repartition_type, line.factor_percent, bool(line.account_id))
            for line in lines.sorted(key)
        ]

    return (
        tax.amount_type == template.amount_type
        and tax.amount == template.amount
        and tax.type_tax_use == template.type_tax_use
        and tax.price_include == template.price_include
        and sig(tax.invoice_repartition_line_ids)
        == sig(template.invoice_repartition_line_ids)
        and sig(tax.refund_repartition_line_ids)
        == sig(template.refund_repartition_line_ids)
    )


def _component_columns(env):
    """(table, column) pairs that store a tax's own one2many children."""
    cols = set()
    for field in env["account.tax"]._fields.values():
        if field.type == "one2many" and field.inverse_name:
            comodel = env[field.comodel_name]
            if comodel._auto and not comodel._abstract and not comodel._transient:
                cols.add((comodel._table, field.inverse_name))
    return cols


def _ref_count(env, tax_id):
    """References that make a duplicated tax unsafe to delete.

    Discovered dynamically from the registry, no table of any module is
    named. Of every way Odoo can link a record, the two that matter for a
    safe unlink are counted:

    - stored many2many: the one channel where a delete loses data silently
      (PostgreSQL cascades the relation rows without a word);
    - stored many2one: fields declaring ondelete set-null/cascade would
      also mutate silently — and one2many needs no leg of its own, its
      storage IS the inverse many2one. (restrict ones would abort the
      update loudly by themselves.)

    The tax's own one2many children (its repartition lines) arrive through
    that same inverse-many2one channel but are components, not references —
    they die with the record — so their columns are excluded; counting them
    made this guard refuse every tax (a real tax always carries repartition
    lines) and the delete branch was unreachable.

    Deliberately NOT counted: soft references (fields.Reference,
    many2one_reference, res_model/res_id pairs, ir.property values) —
    standard Odoo deletion does not guard them either and their orphans
    are inert; and textual/serialized ids (filter domains, action code),
    which are not structural. Abstract/transient models and SQL views are
    skipped.
    """
    cr = env.cr
    excluded = _component_columns(env)
    total = 0
    seen_m2m = set()
    for model_name in env.registry:
        model = env[model_name]
        if model._abstract or model._transient or not model._auto:
            continue
        for field in model._fields.values():
            if not field.store or field.comodel_name != "account.tax":
                continue
            if field.type == "many2one":
                if (model._table, field.name) in excluded:
                    continue
                table, column = model._table, field.name
            elif field.type == "many2many":
                if (field.relation, field.column2) in seen_m2m:
                    continue
                seen_m2m.add((field.relation, field.column2))
                table, column = field.relation, field.column2
            else:
                continue
            cr.execute(
                'SELECT count(*) FROM "{}" WHERE "{}" = %s'.format(table, column),
                (tax_id,),
            )
            total += cr.fetchone()[0]
    return total


def migrate(cr, version):
    """Deduplicate the 5% non-deductible tax against l10n_es.

    The own template (oxigen_l10n_es.account_tax_template_p_iva5_nd) predates
    the official one and is dropped by this version. Per company holding a tax
    born from the own template:

    - official tax MISSING: the existing record is the real historical tax of
      the company, so it simply BECOMES the official one (xml-id module
      switch; nothing else is touched);
    - official tax PRESENT (both templates were instantiated): the duplicate
      must be unused, it is deleted and the official stays.

    The own template row itself is garbage-collected by this same update (its
    xml-id is noupdate=False and the record left the data files); its SII map
    membership is replaced by the official ref in data/aeat_sii_map_data.xml.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    template = env.ref("l10n_es." + TEMPLATE_KEY)
    imd_model = env["ir.model.data"]
    clone_imds = imd_model.search(
        [("module", "=", "oxigen_l10n_es"), ("model", "=", "account.tax")]
    ).filtered(lambda d: d.name.endswith("_" + TEMPLATE_KEY))
    for imd in clone_imds:
        tax = env["account.tax"].browse(imd.res_id).exists()
        if not tax:
            imd.unlink()
            continue
        official_imd = imd_model.search(
            [
                ("module", "=", "l10n_es"),
                ("model", "=", "account.tax"),
                ("name", "=", imd.name),
            ]
        )
        if official_imd:
            refs = _ref_count(env, tax.id)
            if refs:
                raise RuntimeError(
                    "p_iva5_nd dedup: tax %s (company %s) duplicates official"
                    " %s but is referenced %s time(s); refusing to delete"
                    % (tax.id, tax.company_id.id, official_imd.res_id, refs)
                )
            _logger.info(
                "p_iva5_nd dedup: deleting unused duplicated tax %s"
                " (company %s); official %s stays",
                tax.id,
                tax.company_id.id,
                official_imd.res_id,
            )
            tax.unlink()
            if imd.exists():
                imd.unlink()
        else:
            if not _same_shape(tax, template):
                raise RuntimeError(
                    "p_iva5_nd dedup: tax %s (company %s) diverges from the"
                    " official definition; refusing to rebadge"
                    % (tax.id, tax.company_id.id)
                )
            _logger.info(
                "p_iva5_nd dedup: rebadging tax %s (company %s) as l10n_es.%s",
                tax.id,
                tax.company_id.id,
                imd.name,
            )
            imd.write({"module": "l10n_es"})
