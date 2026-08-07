# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
"""Install/uninstall hooks that keep the Detectability relabel reversible.

This addon only changes *wording*: it presents the third hazard-risk factor as
"Detectability" instead of "Occupation / Usage" in the field labels, the
master-data action/menu, and the risk-formula descriptions, in English plus the
Catalan and Spanish translations. It changes nothing technical (field names,
XML IDs, formulas, calculation).

The wording it overrides belongs to the dependency modules ``mgmtsystem_hazard``
and ``mgmtsystem_hazard_risk``. Overriding records you do not own needs an
explicit lifecycle contract, because Odoo does NOT undo those overrides for you
when an *extension* module is uninstalled. The contract guaranteed here (each
case verified on a real database):

* INSTALL    -> every label/description shows "Detectability" in EN/ES/CA.
* CHILD -u   -> the relabel survives: the addon data is re-applied and the
               translations are already stored.
* PARENT -u  -> the relabel survives: upgrading a dependency makes Odoo
               cascade-upgrade this (dependent) addon, which re-applies last.
* UNINSTALL  -> the Oxigen-specific relabel disappears, and the generic
               mgmtsystem_hazard_risk_extension translations become visible
               again for the risk formulas.

Design rules honoured here:

* No copied wording in Python hooks. The visible strings live in this addon's
  field definitions, data, and PO files; on uninstall the originals are
  restored by re-applying the *owners' own* source, never by copying their
  strings into this hook.
* No SQL.
"""

import logging

from odoo import SUPERUSER_ID, api
from odoo.tools.convert import convert_file

_logger = logging.getLogger(__name__)

_MODULE = "oxigen_mgmtsystem_hazard_risk_extension"
_GENERIC_MODULE = "mgmtsystem_hazard_risk_extension"
_DESCRIPTION_NAME = "mgmtsystem.hazard.risk.computation,description"
_TRANSLATION_LANGS = ("ca_ES", "es_ES")

# The dependency modules that own every record this addon relabels.
_OWNER_MODULES = ("mgmtsystem_hazard", "mgmtsystem_hazard_risk")
_TRANSLATION_RESTORE_MODULES = _OWNER_MODULES + (_GENERIC_MODULE,)

# Navigation records (owned by mgmtsystem_hazard) whose translations this addon
# forces. Referenced by XML ID only -- no wording is copied here. Listed so the
# uninstall hook can drop the values forced onto them for the languages the
# owner ships empty (see uninstall_hook, STEP 1).
_OWNER_NAV_XMLIDS = (
    "mgmtsystem_hazard.open_mgmtsystem_hazard_usage_list",
    "mgmtsystem_hazard.menu_open_hazard_usage",
)

# Owner data file whose records are shipped as ``noupdate="1"`` (the risk
# formula descriptions). A normal module *upgrade* never re-applies noupdate
# records, so the uninstall hook reloads this one file in "init" mode to restore
# them from the owner's own source (see uninstall_hook, STEP 2).
_OWNER_NOUPDATE_DATA = (
    "mgmtsystem_hazard_risk",
    "data/mgmtsystem_hazard_risk_computation.xml",
)
_FORMULA_XMLIDS = (
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_times_c",
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_plus_c",
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_times_c",
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_plus_c",
)
_FIELD_LABEL_TRANSLATION_LANG = "en_US"
_FIELD_LABELS = (
    ("mgmtsystem.hazard", "usage_id"),
    ("mgmtsystem.hazard.usage", "name"),
    ("mgmtsystem.hazard.residual_risk", "usage_id"),
)
_FIELD_LABEL_MODELS = (
    "mgmtsystem.hazard",
    "mgmtsystem.hazard.usage",
    "mgmtsystem.hazard.residual_risk",
)


def _formula_ids(env):
    return [
        record.id
        for record in (
            env.ref(xmlid, raise_if_not_found=False) for xmlid in _FORMULA_XMLIDS
        )
        if record
    ]


def _delete_formula_translations(env, langs=None):
    langs = langs or _TRANSLATION_LANGS
    formula_ids = _formula_ids(env)
    if formula_ids:
        env["ir.translation"].search(
            [
                ("type", "=", "model"),
                ("name", "=", _DESCRIPTION_NAME),
                ("res_id", "in", formula_ids),
                ("lang", "in", langs),
            ]
        ).unlink()


def _reflect_field_labels(cr, registry):
    """Persist inherited string= overrides in ir.model.fields for fields_get()."""
    registry.init_models(cr, _FIELD_LABEL_MODELS, {"module": _MODULE}, install=False)


def _set_english_field_label_translations(env):
    field_model = env["ir.model.fields"]
    for model_name, field_name in _FIELD_LABELS:
        field_record = field_model._get(model_name, field_name)
        if not field_record:
            continue
        label = env[model_name]._fields[field_name].string
        _set_english_record_translation(env, field_record, "field_description", label)


def _set_english_record_translation(env, record, field_name, value=None):
    value = value if value is not None else record[field_name]
    name = "%s,%s" % (record._name, field_name)
    translation = env["ir.translation"]
    translation._set_ids(
        name,
        "model",
        _FIELD_LABEL_TRANSLATION_LANG,
        record.ids,
        value,
        src=value,
    )
    translation.search(
        [
            ("name", "=", name),
            ("res_id", "=", record.id),
            ("lang", "=", _FIELD_LABEL_TRANSLATION_LANG),
        ]
    ).write({"module": _MODULE})


def _set_english_owner_record_translations(env):
    for xmlid in _OWNER_NAV_XMLIDS:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            _set_english_record_translation(env, record, "name")
    for xmlid in _FORMULA_XMLIDS:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            _set_english_record_translation(env, record, "description")


def apply_detectability_translations(env, lang=None):
    """Reload this addon's wording after Odoo reloads dependency translations."""
    if lang and lang not in _TRANSLATION_LANGS:
        return
    langs = (lang,) if lang else _TRANSLATION_LANGS
    env["ir.translation"].clear_caches()
    _set_english_field_label_translations(env)
    _set_english_owner_record_translations(env)
    env["ir.translation"].clear_caches()
    _delete_formula_translations(env, langs)
    env["ir.module.module"].search(
        [
            ("name", "=", _MODULE),
            ("state", "in", ("installed", "to install", "to upgrade")),
        ]
    )._update_translations(filter_lang=lang, overwrite=True)
    env["ir.translation"].clear_caches()


def post_init_hook(cr, _registry):
    """Make this addon's translations win over the dependency's, on install.

    WHY this is needed: when a module is installed, Odoo loads its PO files with
    ``overwrite=False``. So for any record the dependency *already* translates
    (the usage field labels, the action/menu name) this addon's PO entry is
    silently ignored and the dependency wording stays -- only the terms the
    dependency never translated come through. The symptom is a relabel that
    "half works" (English changes, Spanish does not).

    The fix is to re-import *this addon's own* translations once more with
    ``overwrite=True`` so the Detectability wording takes precedence while the
    addon is installed. English entries are derived from the already-loaded
    field/data values, not copied into this hook. They then persist through this
    addon's own updates (a ``-u`` does not re-run post_init, but it does not
    undo them).
    """
    _reflect_field_labels(cr, _registry)
    env = api.Environment(cr, SUPERUSER_ID, {})
    apply_detectability_translations(env)


def uninstall_hook(cr, _registry):
    """Put every overridden record back to the dependency's own original value.

    Odoo does NOT revert overrides of records owned by another module when an
    extension of that module is uninstalled, so this hook restores them -- by
    re-applying the owners' own source, copying no wording and running no SQL.
    Three steps, each fixing a specific Odoo behaviour.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    translation = env["ir.translation"]

    # STEP 1 -- Drop the translations this addon forced.
    #
    # WHY: STEP 3 restores the owners' translations, but it cannot clear a value
    # forced into a language the owner ships *empty*: re-importing a PO whose
    # msgstr is empty is a no-op, so the forced value would linger (e.g. the
    # Catalan action/menu name). Also, uninstalling a module does not delete the
    # translations it created on records owned by *another* module (foreign
    # res_id), so this addon's rows on the owner field labels would be orphaned.
    #
    # So we delete (a) every translation attributed to this addon and (b) every
    # translation on the navigation records and formulas it forced (by XML ID).
    # They then fall back to the owner's/generic addon's own values, restored in
    # STEP 3.
    translation.search([("module", "=", _MODULE)]).unlink()
    for xmlid in _OWNER_NAV_XMLIDS:
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            translation.search(
                [("name", "=", "%s,name" % record._name), ("res_id", "=", record.id)]
            ).unlink()
    _delete_formula_translations(env)

    # STEP 2 -- Reload the owner's ``noupdate`` data from its own file.
    #
    # WHY: the risk formula descriptions are shipped by the owner as
    # ``noupdate="1"``. The owner-module upgrade triggered in STEP 3 runs in
    # "update" mode, which by definition SKIPS noupdate records -- so on its own
    # it would NOT restore the formula text this addon changed. Reloading just
    # that one owner file in ``mode="init"`` bypasses the noupdate skip and
    # rewrites those records from the owner's own data file (no wording copied).
    module, filename = _OWNER_NOUPDATE_DATA
    convert_file(cr, module, filename, {}, mode="init", noupdate=False, kind="data")

    # STEP 3 -- Enforce an update of the owner modules.
    #
    # WHY: this is what restores the field LABELS, the action/menu name and the
    # owners' translations, all from the owners' own source:
    #
    #  * Right after this hook returns Odoo uninstalls this addon and then runs
    #    a recursive registry reload (odoo/modules/loading.py, STEP 5). Because
    #    the owner modules are now flagged "to upgrade", that reload re-applies
    #    their data AND re-reflects their fields. Field labels come from Python
    #    ``string=`` and only change on a module update; crucially, by the time
    #    of that reload this addon is already gone, so the labels reflect back to
    #    the owner's "Occupation / Usage" -- no SQL, no hardcoded value.
    #    (``button_upgrade`` only flags the modules; the work happens in that
    #    built-in post-uninstall reload.)
    #  * ``_update_translations(overwrite=True)`` then re-imports the owners' own
    #    PO files over anything still forced, restoring their translations.
    modules = env["ir.module.module"].search(
        [("name", "in", _TRANSLATION_RESTORE_MODULES), ("state", "=", "installed")]
    )
    if modules:
        _logger.info(
            "Enforcing an update of %s to restore the original wording modified "
            "by %s, which is being uninstalled.",
            ", ".join(modules.mapped("name")),
            _MODULE,
        )
        owners = modules.filtered(lambda module: module.name in _OWNER_MODULES)
        owners.button_upgrade()
        modules._update_translations(overwrite=True)
