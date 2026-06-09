# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api

# Strings introduced by this addon that the uninstall hook restores to the
# upstream values. The hook is defensive: it only reverts a record/field when
# its current value matches the addon's expected value, so user-edited values
# are preserved.

_OUR_ACTION_NAME = "Detectabilities"
_OUR_MENU_NAME = "Detectabilities"
_OUR_USAGE_NAME_FIELD_LABEL = "Detectability"

_ORIGINAL_ACTION_NAME = "Occupations / Usages"
_ORIGINAL_MENU_NAME = "Occupations / Usages"
_ORIGINAL_USAGE_NAME_FIELD_LABEL = "Occupation / Usage"

_ORIGINAL_FORMULA_DESCRIPTIONS = {
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_times_c": (
        "Risk = Probability (A) x Severity (B) x Usage (C)"
    ),
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_plus_c": (
        "Risk = ( Probability (A) x Severity (B) ) + Usage (C)"
    ),
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_times_c": (
        "Risk = ( Probability (A) + Severity (B) ) x Usage (C)"
    ),
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_plus_c": (
        "Risk = Probability (A) + Severity (B) + Usage (C)"
    ),
}


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    action = env.ref(
        "mgmtsystem_hazard.open_mgmtsystem_hazard_usage_list",
        raise_if_not_found=False,
    )
    if action and action.name == _OUR_ACTION_NAME:
        action.name = _ORIGINAL_ACTION_NAME

    menu = env.ref(
        "mgmtsystem_hazard.menu_open_hazard_usage",
        raise_if_not_found=False,
    )
    if menu and menu.name == _OUR_MENU_NAME:
        menu.name = _ORIGINAL_MENU_NAME

    for xmlid, original in _ORIGINAL_FORMULA_DESCRIPTIONS.items():
        record = env.ref(xmlid, raise_if_not_found=False)
        if record:
            addon_value = original.replace("Usage (C)", "Detectability (C)")
            if record.description == addon_value:
                record.description = original

    cr.execute(
        """
        UPDATE ir_model_fields
           SET field_description = %s
         WHERE model = 'mgmtsystem.hazard.usage'
           AND name = 'name'
           AND field_description = %s
        """,
        (_ORIGINAL_USAGE_NAME_FIELD_LABEL, _OUR_USAGE_NAME_FIELD_LABEL),
    )

    cr.execute(
        """
        DELETE FROM ir_translation
         WHERE module = 'oxigen_mgmtsystem_hazard_risk'
            OR src IN ('Detectability', 'Detectabilities')
            OR (name IN ('ir.actions.act_window,name',
                         'ir.ui.menu,name',
                         'ir.ui.view,arch_db')
                AND value IN ('Detectabilitat', 'Detectabilitats',
                              'Detectabilidad', 'Detectabilidades'))
            OR (name = 'mgmtsystem.hazard.risk.computation,description'
                AND (src LIKE %s
                     OR value LIKE %s
                     OR value LIKE %s))
        """,
        (
            "%Detectability (C)",
            "%Detectabilitat (C)",
            "%Detectabilidad (C)",
        ),
    )
