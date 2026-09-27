# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_woocommerce.tests.common import (
    PLACEHOLDER,
    TEXT,
    BlankHtmlMigrationMixin,
)
from odoo.addons.connector_woocommerce_wpml.tests.common import WooCommerceWPMLCase


class TestReexportBlankHtmlACF(BlankHtmlMigrationMixin, WooCommerceWPMLCase):
    def test_only_bound_placeholder_in_export_language(self):
        english = self.template.with_context(lang="en_US")
        spanish = self.template.with_context(lang="es_ES")
        english.technical_features = TEXT
        spanish.technical_features = PLACEHOLDER
        self.unbound_template.technical_features = PLACEHOLDER
        content = self._create_template("Real technical features", 1002)
        content.technical_features = TEXT
        self._start_incremental_exports()
        self._run_migration(
            "oxigen_connector_woocommerce_wpml_acf", "14.0.1.0.1", "14.0.1.0.0"
        )
        self._assert_export_selection(
            "woocommerce.product.template",
            self.backend.export_product_tmpl_since,
            self.template,
        )
        self.assertEqual(english.technical_features, TEXT)
        self.assertEqual(spanish.technical_features, PLACEHOLDER)
        self.assertEqual(self.unbound_template.technical_features, PLACEHOLDER)
        self.assertEqual(content.technical_features, TEXT)

    def test_variable_template_reaches_the_variant_batch(self):
        template = self._create_variable_template()
        template.technical_features = PLACEHOLDER
        self._start_incremental_exports()
        self._run_migration(
            "oxigen_connector_woocommerce_wpml_acf", "14.0.1.0.1", "14.0.1.0.0"
        )
        self._assert_export_selection(
            "woocommerce.product.product",
            self.backend.export_products_since,
            template.product_variant_ids,
        )
