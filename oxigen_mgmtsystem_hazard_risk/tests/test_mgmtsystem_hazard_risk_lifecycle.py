# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase, standalone, tagged
from odoo.tools.misc import mute_logger

MODULE = "oxigen_mgmtsystem_hazard_risk"
LANGUAGES = ("es_ES", "ca_ES")

FORMULA_XMLIDS = (
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_times_c",
    "mgmtsystem_hazard_risk.risk_computation_a_times_b_plus_c",
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_times_c",
    "mgmtsystem_hazard_risk.risk_computation_a_plus_b_plus_c",
)

DETECTABILITY = {
    "en_US": {
        "field": "Detectability",
        "list": "Detectabilities",
        "formula_word": "Detectability",
    },
    "es_ES": {
        "field": "Detectabilidad",
        "list": "Detectabilidades",
        "formula_word": "Detectabilidad",
    },
    "ca_ES": {
        "field": "Detectabilitat",
        "list": "Detectabilitats",
        "formula_word": "Detectabilitat",
    },
}

ORIGINAL = {
    "en_US": {
        "field": "Occupation / Usage",
        "list": "Occupations / Usages",
        "formula_word": "Usage",
    },
    "es_ES": {
        "field": "Ocupación / Uso",
        "list": "Ocupaciones / Usos",
        "formula_word": "Usage",
    },
    "ca_ES": {
        "field": "Occupation / Usage",
        "list": "Occupations / Usages",
        "formula_word": "Usage",
    },
}


def _module(env, name):
    module = env["ir.module.module"].search([("name", "=", name)], limit=1)
    assert module, "Module %s must exist" % name
    return module


def _install_languages(env):
    for lang in LANGUAGES:
        with mute_logger("odoo.addons.base.models.ir_translation"):
            env["base.language.install"].create(
                {"lang": lang, "overwrite": True}
            ).lang_install()


def _refresh(env):
    env.reset()
    return env()


def _field_label(env, model_name, field_name, lang):
    return (
        env[model_name]
        .with_context(lang=lang)
        .fields_get([field_name])[field_name]["string"]
    )


def _assert_equal(actual, expected, label):
    assert actual == expected, "%s: expected %r, got %r" % (label, expected, actual)


def _assert_visible_wording(env, expected):
    action = env.ref("mgmtsystem_hazard.open_mgmtsystem_hazard_usage_list")
    menu = env.ref("mgmtsystem_hazard.menu_open_hazard_usage")
    for lang, values in expected.items():
        _assert_equal(
            _field_label(env, "mgmtsystem.hazard", "usage_id", lang),
            values["field"],
            "%s mgmtsystem.hazard usage_id label" % lang,
        )
        _assert_equal(
            _field_label(env, "mgmtsystem.hazard.usage", "name", lang),
            values["field"],
            "%s mgmtsystem.hazard.usage name label" % lang,
        )
        _assert_equal(
            _field_label(env, "mgmtsystem.hazard.residual_risk", "usage_id", lang),
            values["field"],
            "%s mgmtsystem.hazard.residual_risk usage_id label" % lang,
        )
        _assert_equal(
            action.with_context(lang=lang).name,
            values["list"],
            "%s hazard usage action name" % lang,
        )
        _assert_equal(
            menu.with_context(lang=lang).name,
            values["list"],
            "%s hazard usage menu name" % lang,
        )
        for xmlid in FORMULA_XMLIDS:
            description = env.ref(xmlid).with_context(lang=lang).description
            assert (
                values["formula_word"] in description
            ), "%s %s description must contain %r, got %r" % (
                lang,
                xmlid,
                values["formula_word"],
                description,
            )


@standalone(MODULE)
def test_mgmtsystem_hazard_risk_lifecycle(env):
    """Exercise the relabel lifecycle through public module operations."""
    _install_languages(env)
    env = _refresh(env)
    _assert_visible_wording(env, DETECTABILITY)

    _module(env, "mgmtsystem_hazard_risk").button_immediate_upgrade()
    env = _refresh(env)
    _assert_visible_wording(env, DETECTABILITY)

    _module(env, MODULE).button_immediate_upgrade()
    env = _refresh(env)
    _assert_visible_wording(env, DETECTABILITY)

    try:
        _module(env, MODULE).button_immediate_uninstall()
        env = _refresh(env)
        _assert_visible_wording(env, ORIGINAL)
    finally:
        env = _refresh(env)
        module = _module(env, MODULE)
        if module.state != "installed":
            module.button_immediate_install()
            env = _refresh(env)

    _assert_visible_wording(env, DETECTABILITY)


@tagged("post_install", "-at_install")
class TestMgmtsystemHazardRiskWording(TransactionCase):
    def test_installed_visible_wording(self):
        _install_languages(self.env)
        self.env.clear()

        _assert_visible_wording(self.env, DETECTABILITY)
