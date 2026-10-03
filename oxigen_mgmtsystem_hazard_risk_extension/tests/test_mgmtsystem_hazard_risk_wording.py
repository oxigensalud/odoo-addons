# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.modules.module import get_module_resource
from odoo.osv import expression
from odoo.tests.common import SavepointCase, new_test_user, tagged

from ..hooks import post_init_hook, uninstall_hook


class TestWordingCommon(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.hazard_label = cls.env.ref(
            "mgmtsystem_hazard.field_mgmtsystem_hazard__usage_id"
        )
        cls.usage_label = cls.env.ref(
            "mgmtsystem_hazard.field_mgmtsystem_hazard_usage__name"
        )
        cls.residual_risk_label = cls.env.ref(
            "mgmtsystem_hazard_risk.field_mgmtsystem_hazard_residual_risk__usage_id"
        )
        cls.action = cls.env.ref("mgmtsystem_hazard.open_mgmtsystem_hazard_usage_list")
        cls.menu = cls.env.ref("mgmtsystem_hazard.menu_open_hazard_usage")
        cls.formula_a_times_b_times_c = cls.env.ref(
            "mgmtsystem_hazard_risk.risk_computation_a_times_b_times_c"
        )
        cls.formula_a_times_b_plus_c = cls.env.ref(
            "mgmtsystem_hazard_risk.risk_computation_a_times_b_plus_c"
        )
        cls.formula_a_plus_b_times_c = cls.env.ref(
            "mgmtsystem_hazard_risk.risk_computation_a_plus_b_times_c"
        )
        cls.formula_a_plus_b_plus_c = cls.env.ref(
            "mgmtsystem_hazard_risk.risk_computation_a_plus_b_plus_c"
        )
        # Start without stored wording, whatever the database holds
        cls._wording_translations().unlink()

    @classmethod
    def _wording_translations(cls):
        """The stored translations, in any language, of the nine texts the
        module relabels."""
        return cls.env["ir.translation"].search(
            [("type", "=", "model")]
            + expression.OR(
                [
                    [
                        ("name", "=", "ir.model.fields,field_description"),
                        (
                            "res_id",
                            "in",
                            [
                                cls.hazard_label.id,
                                cls.usage_label.id,
                                cls.residual_risk_label.id,
                            ],
                        ),
                    ],
                    [
                        ("name", "=", "ir.actions.act_window,name"),
                        ("res_id", "=", cls.action.id),
                    ],
                    [("name", "=", "ir.ui.menu,name"), ("res_id", "=", cls.menu.id)],
                    [
                        ("name", "=", "mgmtsystem.hazard.risk.computation,description"),
                        (
                            "res_id",
                            "in",
                            [
                                cls.formula_a_times_b_times_c.id,
                                cls.formula_a_times_b_plus_c.id,
                                cls.formula_a_plus_b_times_c.id,
                                cls.formula_a_plus_b_plus_c.id,
                            ],
                        ),
                    ],
                ]
            )
        )

    def _read_wording(self, lang):
        """The nine texts the module relabels, as a user reads them in
        ``lang`` (a label is the field description fields_get shows)."""
        return {
            "hazard label": self.hazard_label.with_context(lang=lang).field_description,
            "usage label": self.usage_label.with_context(lang=lang).field_description,
            "residual risk label": self.residual_risk_label.with_context(
                lang=lang
            ).field_description,
            "action": self.action.with_context(lang=lang).name,
            "menu": self.menu.with_context(lang=lang).name,
            "A * B * C": self.formula_a_times_b_times_c.with_context(
                lang=lang
            ).description,
            "(A * B) + C": self.formula_a_times_b_plus_c.with_context(
                lang=lang
            ).description,
            "(A + B) * C": self.formula_a_plus_b_times_c.with_context(
                lang=lang
            ).description,
            "A + B + C": self.formula_a_plus_b_plus_c.with_context(
                lang=lang
            ).description,
        }

    def _store_translation(self, record, field_name, lang, value):
        """Store a translation of a record's text, created or replaced, as Odoo
        stores one, without writing the text itself: the label of a field
        defined in code cannot be written through the field."""
        self.env["ir.translation"]._set_ids(
            "%s,%s" % (record._name, field_name),
            "model",
            lang,
            record.ids,
            value,
            record[field_name],
        )


@tagged("post_install", "-at_install")
class TestTranslationHooks(TestWordingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["res.lang"]._activate_lang("es_ES")
        cls.env["res.lang"]._activate_lang("ca_ES")
        dependencies = cls.env["ir.module.module"].search(
            [
                (
                    "name",
                    "in",
                    [
                        "mgmtsystem_hazard",
                        "mgmtsystem_hazard_risk",
                        "mgmtsystem_hazard_risk_extension",
                    ],
                )
            ]
        )
        dependencies._update_translations(["es_ES", "ca_ES"])

    def test_install_replaces_stored_translations(self):
        self.assertEqual(
            self._read_wording("es_ES"),
            {
                "hazard label": "Ocupación / Uso",
                "usage label": "Ocupación / Uso",
                "residual risk label": "Ocupación / Uso",
                "action": "Ocupaciones / Usos",
                "menu": "Ocupaciones / Usos",
                "A * B * C": "Riesgo = Probabilidad (A) x Severidad (B) x Uso (C)",
                "(A * B) + C": "Riesgo = ( Probabilidad (A) x Severidad (B) ) "
                "+ Uso (C)",
                "(A + B) * C": "Riesgo = ( Probabilidad (A) + Severidad (B) ) "
                "x Uso (C)",
                "A + B + C": "Riesgo = Probabilidad (A) + Severidad (B) + Uso (C)",
            },
        )
        # Catalan typed by hand where the dependencies leave the text untranslated
        self._store_translation(
            self.hazard_label, "field_description", "ca_ES", "Stored wording"
        )
        self._store_translation(
            self.usage_label, "field_description", "ca_ES", "Stored wording"
        )
        self._store_translation(
            self.residual_risk_label, "field_description", "ca_ES", "Stored wording"
        )
        self.action.with_context(lang="ca_ES").name = "Stored wording"
        self.menu.with_context(lang="ca_ES").name = "Stored wording"
        post_init_hook(self.env.cr, self.registry)
        self.assertEqual(
            self._read_wording("es_ES"),
            {
                "hazard label": "Detectabilidad",
                "usage label": "Detectabilidad",
                "residual risk label": "Detectabilidad",
                "action": "Detectabilidades",
                "menu": "Detectabilidades",
                "A * B * C": "Riesgo = Probabilidad (A) x Severidad (B) "
                "x Detectabilidad (C)",
                "(A * B) + C": "Riesgo = ( Probabilidad (A) x Severidad (B) ) "
                "+ Detectabilidad (C)",
                "(A + B) * C": "Riesgo = ( Probabilidad (A) + Severidad (B) ) "
                "x Detectabilidad (C)",
                "A + B + C": "Riesgo = Probabilidad (A) + Severidad (B) "
                "+ Detectabilidad (C)",
            },
        )
        self.assertEqual(
            self._read_wording("ca_ES"),
            {
                "hazard label": "Detectabilitat",
                "usage label": "Detectabilitat",
                "residual risk label": "Detectabilitat",
                "action": "Detectabilitats",
                "menu": "Detectabilitats",
                "A * B * C": "Risc = Probabilitat (A) x Severitat (B) "
                "x Detectabilitat (C)",
                "(A * B) + C": "Risc = ( Probabilitat (A) x Severitat (B) ) "
                "+ Detectabilitat (C)",
                "(A + B) * C": "Risc = ( Probabilitat (A) + Severitat (B) ) "
                "x Detectabilitat (C)",
                "A + B + C": "Risc = Probabilitat (A) + Severitat (B) "
                "+ Detectabilitat (C)",
            },
        )

    def test_install_removes_english_translations(self):
        # The English copies an English edit made before the install leaves
        self._store_translation(
            self.hazard_label, "field_description", "en_US", "Edited by hand"
        )
        self._store_translation(
            self.formula_a_times_b_times_c, "description", "en_US", "Edited by hand"
        )
        post_init_hook(self.env.cr, self.registry)
        self.assertNotIn("en_US", self._wording_translations().mapped("lang"))
        self.assertEqual(
            self._read_wording("en_US"),
            {
                "hazard label": "Detectability",
                "usage label": "Detectability",
                "residual risk label": "Detectability",
                "action": "Detectabilities",
                "menu": "Detectabilities",
                "A * B * C": "Risk = Probability (A) x Severity (B) "
                "x Detectability (C)",
                "(A * B) + C": "Risk = ( Probability (A) x Severity (B) ) "
                "+ Detectability (C)",
                "(A + B) * C": "Risk = ( Probability (A) + Severity (B) ) "
                "x Detectability (C)",
                "A + B + C": "Risk = Probability (A) + Severity (B) "
                "+ Detectability (C)",
            },
        )

    def test_uninstall_gives_back_dependencies_wording(self):
        post_init_hook(self.env.cr, self.registry)
        uninstall_hook(self.env.cr, self.registry)
        self.assertEqual(
            self._read_wording("es_ES"),
            {
                "hazard label": "Ocupación / Uso",
                "usage label": "Ocupación / Uso",
                "residual risk label": "Ocupación / Uso",
                "action": "Ocupaciones / Usos",
                "menu": "Ocupaciones / Usos",
                "A * B * C": "Riesgo = Probabilidad (A) x Severidad (B) x Uso (C)",
                "(A * B) + C": "Riesgo = ( Probabilidad (A) x Severidad (B) ) "
                "+ Uso (C)",
                "(A + B) * C": "Riesgo = ( Probabilidad (A) + Severidad (B) ) "
                "x Uso (C)",
                "A + B + C": "Riesgo = Probabilidad (A) + Severidad (B) + Uso (C)",
            },
        )
        # The dependencies leave the labels and the names untranslated in
        # Catalan: they show their source until the owners are upgraded
        self.assertEqual(
            self._read_wording("ca_ES"),
            {
                "hazard label": "Detectability",
                "usage label": "Detectability",
                "residual risk label": "Detectability",
                "action": "Detectabilities",
                "menu": "Detectabilities",
                "A * B * C": "Risc = Probabilitat (A) x Severitat (B) x Ús (C)",
                "(A * B) + C": "Risc = ( Probabilitat (A) x Severitat (B) ) + Ús (C)",
                "(A + B) * C": "Risc = ( Probabilitat (A) + Severitat (B) ) x Ús (C)",
                "A + B + C": "Risc = Probabilitat (A) + Severitat (B) + Ús (C)",
            },
        )
        # mgmtsystem_hazard owns the hazard and usage labels, the action and
        # the menu. Its published package ships an English PO file, which
        # gives them back at once; its 14.0 branch ships none, and then they
        # show their source until the owner is upgraded
        if get_module_resource("mgmtsystem_hazard", "i18n", "en.po"):
            label, names = "Occupation / Usage", "Occupations / Usages"
        else:
            label, names = "Detectability", "Detectabilities"
        self.assertEqual(
            self._read_wording("en_US"),
            {
                "hazard label": label,
                "usage label": label,
                "residual risk label": "Detectability",
                "action": names,
                "menu": names,
                "A * B * C": "Risk = Probability (A) x Severity (B) x Usage (C)",
                "(A * B) + C": "Risk = ( Probability (A) x Severity (B) ) + Usage (C)",
                "(A + B) * C": "Risk = ( Probability (A) + Severity (B) ) x Usage (C)",
                "A + B + C": "Risk = Probability (A) + Severity (B) + Usage (C)",
            },
        )

    def test_uninstall_upgrades_no_module(self):
        post_init_hook(self.env.cr, self.registry)
        uninstall_hook(self.env.cr, self.registry)
        self.assertFalse(
            self.env["ir.module.module"].search([("state", "=", "to upgrade")])
        )

    def test_uninstall_keeps_other_formulas(self):
        formula = self.env.ref("mgmtsystem_hazard_risk.risk_computation_a_times_b")
        post_init_hook(self.env.cr, self.registry)
        formula.with_context(lang="en_US").description = "Edited by hand"
        formula.with_context(lang="es_ES").description = "Translated by hand"
        uninstall_hook(self.env.cr, self.registry)
        self.assertEqual(formula.description, "Edited by hand")
        self.assertEqual(
            formula.with_context(lang="es_ES").description, "Translated by hand"
        )

    def test_uninstall_keeps_translation_of_language_not_shipped(self):
        formula = self.formula_a_times_b_times_c
        post_init_hook(self.env.cr, self.registry)
        self.env["res.lang"]._activate_lang("fr_FR")
        self._store_translation(
            self.hazard_label, "field_description", "fr_FR", "Written by hand"
        )
        formula.with_context(lang="fr_FR").description = "Written by hand"
        uninstall_hook(self.env.cr, self.registry)
        wording = self._read_wording("fr_FR")
        self.assertEqual(wording["hazard label"], "Written by hand")
        self.assertEqual(wording["A * B * C"], "Written by hand")

    def test_uninstall_keeps_english_edited_by_hand(self):
        formula = self.formula_a_times_b_times_c
        post_init_hook(self.env.cr, self.registry)
        formula.with_context(lang="en_US").description = "Edited by hand"
        uninstall_hook(self.env.cr, self.registry)
        self.assertEqual(formula.description, "Edited by hand")

    def test_uninstall_keeps_translations_of_other_records(self):
        # A model the module extends, and a label of it the module does not change
        model = self.env["ir.model"]._get("ir.translation")
        label = self.env.ref("base.field_ir_translation__display_name")
        post_init_hook(self.env.cr, self.registry)
        model.with_context(lang="es_ES").name = "Translated by hand"
        self._store_translation(
            label, "field_description", "es_ES", "Translated by hand"
        )
        uninstall_hook(self.env.cr, self.registry)
        self.assertEqual(model.with_context(lang="es_ES").name, "Translated by hand")
        self.assertEqual(
            label.with_context(lang="es_ES").field_description, "Translated by hand"
        )

    def test_uninstall_skips_deleted_formula(self):
        formula = self.formula_a_times_b_plus_c
        post_init_hook(self.env.cr, self.registry)
        self.formula_a_times_b_times_c.unlink()
        uninstall_hook(self.env.cr, self.registry)
        self.assertEqual(
            formula.description, "Risk = ( Probability (A) x Severity (B) ) + Usage (C)"
        )
        self.assertEqual(
            formula.with_context(lang="es_ES").description,
            "Riesgo = ( Probabilidad (A) x Severidad (B) ) + Uso (C)",
        )


@tagged("post_install", "-at_install")
class TestLanguageInstall(TestWordingCommon):
    def test_language_install_gives_module_wording(self):
        administrator = self.env.ref("base.user_admin")
        self.env["base.language.install"].with_user(administrator).create(
            {"lang": "es_ES"}
        ).lang_install()
        self.assertEqual(
            self._read_wording("es_ES"),
            {
                "hazard label": "Detectabilidad",
                "usage label": "Detectabilidad",
                "residual risk label": "Detectabilidad",
                "action": "Detectabilidades",
                "menu": "Detectabilidades",
                "A * B * C": "Riesgo = Probabilidad (A) x Severidad (B) "
                "x Detectabilidad (C)",
                "(A * B) + C": "Riesgo = ( Probabilidad (A) x Severidad (B) ) "
                "+ Detectabilidad (C)",
                "(A + B) * C": "Riesgo = ( Probabilidad (A) + Severidad (B) ) "
                "x Detectabilidad (C)",
                "A + B + C": "Riesgo = Probabilidad (A) + Severidad (B) "
                "+ Detectabilidad (C)",
            },
        )

    def test_language_install_by_settings_administrator(self):
        self.env["res.lang"]._activate_lang("es_ES")
        administrator = new_test_user(
            self.env,
            login="settings_admin_hazard_test",
            groups="base.group_system",
            lang="es_ES",
        )
        self.env["base.language.install"].with_user(administrator).with_context(
            lang="es_ES"
        ).create({"lang": "es_ES"}).lang_install()
        self.assertEqual(
            self._read_wording("en_US"),
            {
                "hazard label": "Detectability",
                "usage label": "Detectability",
                "residual risk label": "Detectability",
                "action": "Detectabilities",
                "menu": "Detectabilities",
                "A * B * C": "Risk = Probability (A) x Severity (B) "
                "x Detectability (C)",
                "(A * B) + C": "Risk = ( Probability (A) x Severity (B) ) "
                "+ Detectability (C)",
                "(A + B) * C": "Risk = ( Probability (A) + Severity (B) ) "
                "x Detectability (C)",
                "A + B + C": "Risk = Probability (A) + Severity (B) "
                "+ Detectability (C)",
            },
        )

    def test_language_install_gives_module_wording_to_spanish_variant(self):
        # A language its Spanish files cover, loaded for the first time
        administrator = self.env.ref("base.user_admin")
        self.env["base.language.install"].with_user(administrator).create(
            {"lang": "es_MX"}
        ).lang_install()
        self.assertEqual(
            self._read_wording("es_MX"),
            {
                "hazard label": "Detectabilidad",
                "usage label": "Detectabilidad",
                "residual risk label": "Detectabilidad",
                "action": "Detectabilidades",
                "menu": "Detectabilidades",
                "A * B * C": "Riesgo = Probabilidad (A) x Severidad (B) "
                "x Detectabilidad (C)",
                "(A * B) + C": "Riesgo = ( Probabilidad (A) x Severidad (B) ) "
                "+ Detectabilidad (C)",
                "(A + B) * C": "Riesgo = ( Probabilidad (A) + Severidad (B) ) "
                "x Detectabilidad (C)",
                "A + B + C": "Riesgo = Probabilidad (A) + Severidad (B) "
                "+ Detectabilidad (C)",
            },
        )

    def test_language_update_replaces_spanish_edit(self):
        formula = self.formula_a_times_b_times_c
        administrator = self.env.ref("base.user_admin")
        self.env["res.lang"]._activate_lang("es_ES")
        post_init_hook(self.env.cr, self.registry)
        formula.with_context(lang="es_ES").description = "Translated by hand"
        self.env["base.language.install"].with_user(administrator).create(
            {"lang": "es_ES"}
        ).lang_install()
        self.assertEqual(
            formula.with_context(lang="es_ES").description,
            "Riesgo = Probabilidad (A) x Severidad (B) x Detectabilidad (C)",
        )

    def test_language_install_skips_deleted_formula(self):
        formula = self.formula_a_times_b_plus_c
        administrator = self.env.ref("base.user_admin")
        self.env["res.lang"]._activate_lang("es_ES")
        post_init_hook(self.env.cr, self.registry)
        self.formula_a_times_b_times_c.unlink()
        formula.with_context(lang="es_ES").description = "Translated by hand"
        self.env["base.language.install"].with_user(administrator).create(
            {"lang": "es_ES"}
        ).lang_install()
        self.assertEqual(
            formula.with_context(lang="es_ES").description,
            "Riesgo = ( Probabilidad (A) x Severidad (B) ) + Detectabilidad (C)",
        )
