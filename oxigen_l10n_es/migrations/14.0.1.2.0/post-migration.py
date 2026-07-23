# Copyright 2026 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

MODULE = "oxigen_l10n_es"
CLONE_POS = "oxigen_fp_extra"
TAI_MODULE = "l10n_es"
TAI_POS = "fp_not_subject_tai"
FPAT_TAI = [
    "fpat_tai_acc_1",
    "fpat_tai_acc_2",
    "fpat_tai_acc_3",
    "fpat_tai_acc_4",
    "fpat_tai_acc_5",
    "fpat_tai_acc_6",
]
# Fields that define the official position's identity and matching
# behavior; the surviving record inherits them from the instance it
# replaces.
IDENTITY_FIELDS = [
    "name",
    "note",
    "sequence",
    "auto_apply",
    "vat_required",
    "country_id",
    "country_group_id",
    "zip_from",
    "zip_to",
]
POSITION_MODEL = "account.fiscal.position"
LINE_MODELS = ("account.fiscal.position.tax", "account.fiscal.position.account")


def _company_record(env, company, template, model):
    """Resolve the company record instantiated from ``template``.

    Match by terminal xml-id name whatever the custody module; more
    than one match is never legitimate, fail loudly.
    """
    xmlid = template.get_external_id().get(template.id)
    if not xmlid:
        return None
    name = "%s_%s" % (company.id, xmlid.split(".", 1)[1])
    imds = env["ir.model.data"].search([("model", "=", model), ("name", "=", name)])
    if len(imds) > 1:
        raise RuntimeError(
            "TAI adoption: ambiguous company record for %s (company %s):"
            " modules %s" % (xmlid, company.id, imds.mapped("module"))
        )
    return env[model].browse(imds.res_id) if imds else None


def _component_columns(env, model):
    """(table, column) pairs that store the model's own one2many children."""
    cols = set()
    for field in env[model]._fields.values():
        if field.type == "one2many" and field.inverse_name:
            comodel = env[field.comodel_name]
            if comodel._auto and not comodel._abstract and not comodel._transient:
                cols.add((comodel._table, field.inverse_name))
    return cols


def _inbound_refs(env, model, rec_id):
    """Count every stored reference to the record, children excluded.

    Discovered dynamically from the registry (no table of any module
    is named): every stored many2one and many2many whose comodel is
    ``model``, plus the ir.property value_reference channel where the
    partner assignments live. The record's own mapping lines are
    components, not references, so their inverse columns are skipped.
    """
    cr = env.cr
    excluded = _component_columns(env, model)
    total = 0
    details = []
    seen_m2m = set()
    for model_name in env.registry:
        m = env[model_name]
        if m._abstract or m._transient or not m._auto:
            continue
        for field in m._fields.values():
            if not field.store or field.comodel_name != model:
                continue
            if field.type == "many2one":
                if (m._table, field.name) in excluded:
                    continue
                table, column = m._table, field.name
            elif field.type == "many2many":
                key = (field.relation, field.column2)
                if key in seen_m2m:
                    continue
                seen_m2m.add(key)
                table, column = field.relation, field.column2
            else:
                continue
            cr.execute(
                'SELECT count(*) FROM "{}" WHERE "{}" = %s'.format(table, column),
                (rec_id,),
            )
            count = cr.fetchone()[0]
            if count:
                total += count
                details.append("%s.%s: %s" % (model_name, field.name, count))
    cr.execute(
        "SELECT count(*) FROM ir_property WHERE value_reference = %s",
        ("%s,%d" % (model, rec_id),),
    )
    count = cr.fetchone()[0]
    if count:
        total += count
        details.append("ir.property: %s" % count)
    return total, details


def _delete_position(env, position):
    """Delete a fiscal position with its lines and every stale xml-id."""
    imd_model = env["ir.model.data"]
    for line_model in LINE_MODELS:
        children = env[line_model].search([("position_id", "=", position.id)])
        if children:
            imd_model.search(
                [("model", "=", line_model), ("res_id", "in", children.ids)]
            ).unlink()
            children.unlink()
    position.unlink()


def _adopt(env, company, clone, clone_imd, official_imd):
    """The clone becomes the official TAI position of the company."""
    imd_model = env["ir.model.data"]
    identity_vals = {}
    if official_imd:
        virgin = env[POSITION_MODEL].browse(official_imd.res_id).exists()
        if virgin:
            refs, details = _inbound_refs(env, POSITION_MODEL, virgin.id)
            if refs:
                raise RuntimeError(
                    "TAI adoption: the official position of company %s is"
                    " referenced %s time(s) (%s); it was expected unused,"
                    " refusing to replace it" % (company.id, refs, "; ".join(details))
                )
            for fname in IDENTITY_FIELDS:
                value = virgin[fname]
                field = virgin._fields[fname]
                identity_vals[fname] = value.id if field.type == "many2one" else value
            _delete_position(env, virgin)
    if not identity_vals:
        template = env.ref("%s.%s" % (TAI_MODULE, TAI_POS))
        identity_vals = {"name": template.name, "note": template.note}
        _logger.warning(
            "TAI adoption: company %s had no official TAI instance; the"
            " adopted position takes the template identity",
            company.id,
        )
    clone.write(identity_vals)
    if official_imd:
        official_imd.write({"res_id": clone.id, "noupdate": True})
    else:
        imd_model.create(
            {
                "module": TAI_MODULE,
                "name": "%s_%s" % (company.id, TAI_POS),
                "model": POSITION_MODEL,
                "res_id": clone.id,
                "noupdate": True,
            }
        )
    clone_imd.unlink()
    # The clone's own line xml-ids die with its identity (the records
    # stay); nothing may keep pointing at retired template names.
    stale = imd_model.search(
        [
            ("module", "=", MODULE),
            ("model", "in", list(LINE_MODELS)),
            "|",
            ("name", "=like", "%s\\_fptt\\_%s\\_%%" % (company.id, CLONE_POS)),
            ("name", "=like", "%s\\_fpat\\_extra\\_acc\\_%%" % company.id),
        ]
    )
    if stale:
        stale.unlink()
    _logger.info(
        "TAI adoption: position %s of company %s now holds the official"
        " identity %s.%s_%s",
        clone.id,
        company.id,
        TAI_MODULE,
        company.id,
        TAI_POS,
    )


def _materialize_account_swaps(env, company, position):
    """Materialize this module's TAI account-swap templates, wizard-style."""
    imd_model = env["ir.model.data"]
    fpat_model = env["account.fiscal.position.account"]
    for tname in FPAT_TAI:
        tmpl = env.ref("%s.%s" % (MODULE, tname))
        src = _company_record(env, company, tmpl.account_src_id, "account.account")
        dest = _company_record(env, company, tmpl.account_dest_id, "account.account")
        if not src or not dest:
            _logger.info(
                "TAI adoption: company %s misses the accounts for %s, skipping",
                company.id,
                tname,
            )
            continue
        if fpat_model.search_count(
            [
                ("position_id", "=", position.id),
                ("account_src_id", "=", src.id),
                ("account_dest_id", "=", dest.id),
            ]
        ):
            continue
        line_name = "%s_%s" % (company.id, tname)
        if imd_model.search_count(
            [
                ("model", "=", "account.fiscal.position.account"),
                ("name", "=", line_name),
            ]
        ):
            continue
        fpat = fpat_model.create(
            {
                "position_id": position.id,
                "account_src_id": src.id,
                "account_dest_id": dest.id,
            }
        )
        imd_model.create(
            {
                "module": MODULE,
                "name": line_name,
                "model": "account.fiscal.position.account",
                "res_id": fpat.id,
                "noupdate": True,
            }
        )
        _logger.info(
            "TAI adoption: materialized %s on the TAI position of company %s",
            tname,
            company.id,
        )


def migrate(cr, version):
    """The position cloned from the TAI adopts the official identity.

    'Oxigen Régimen Extracomunitario / Canarias, Ceuta y Melilla' was
    born in 2022 as a clone of the official 'No sujeto por reglas de
    localización (TAI)' position instead of an extension of it. The
    clone is the record that carries the company history (posted
    entries and the partner assignments point at it) while the
    official instance was never used by anything, so instead of moving
    history around, the identities swap:

    - the official (unused, asserted so) instance is deleted with its
      lines and their xml-ids;
    - the clone record inherits the official identity: its fields, the
      official xml-id (kept noupdate) and the official name. History
      and partner assignments are untouched because the record itself
      survives;
    - the clone xml-ids (position and lines) are dropped: the records
      now live under the official identity, governed at template level
      by l10n_es, l10n_es_special_prorate, l10n_es_extension and this
      module's account swaps;
    - the account-swap templates this version declares on the official
      TAI are materialized on companies that miss them (the adopted
      positions already carry them).

    The clone position template leaves the data files with this
    version and is dropped by the update's own cleanup. On a fresh
    install this script never runs. Idempotent: an already-adopted
    company is skipped.
    """
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    imd_model = env["ir.model.data"]
    for company in env["res.company"].search([]):
        clone_imd = imd_model.search(
            [
                ("module", "=", MODULE),
                ("model", "=", POSITION_MODEL),
                ("name", "=", "%s_%s" % (company.id, CLONE_POS)),
            ]
        )
        official_imd = imd_model.search(
            [
                ("module", "=", TAI_MODULE),
                ("model", "=", POSITION_MODEL),
                ("name", "=", "%s_%s" % (company.id, TAI_POS)),
            ]
        )
        if clone_imd:
            clone = env[POSITION_MODEL].browse(clone_imd.res_id).exists()
            if not clone:
                clone_imd.unlink()
            elif official_imd and official_imd.res_id == clone.id:
                pass  # already adopted
            else:
                _adopt(env, company, clone, clone_imd, official_imd)
                official_imd = imd_model.search(
                    [
                        ("module", "=", TAI_MODULE),
                        ("model", "=", POSITION_MODEL),
                        ("name", "=", "%s_%s" % (company.id, TAI_POS)),
                    ]
                )
        if official_imd:
            position = env[POSITION_MODEL].browse(official_imd.res_id).exists()
            if position:
                _materialize_account_swaps(env, company, position)

    # Nothing may survive under the retired identity.
    remaining = imd_model.search_count(
        [
            ("module", "=", MODULE),
            ("model", "=", POSITION_MODEL),
            ("name", "=like", "%%\\_%s" % CLONE_POS),
        ]
    )
    if remaining:
        raise RuntimeError(
            "TAI adoption: %s positions still carry the %s.%s identity"
            % (remaining, MODULE, CLONE_POS)
        )
