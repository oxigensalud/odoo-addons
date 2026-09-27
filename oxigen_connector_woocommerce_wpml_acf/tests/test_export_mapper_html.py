# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_woocommerce.tests.common import PLACEHOLDER, TEXT, TEXT_HEX
from odoo.addons.connector_woocommerce_wpml.tests.common import WooCommerceWPMLCase


class TestExportMapperHtmlACF(WooCommerceWPMLCase):
    """Technical features go to the ACF meta: text kept, a blank value clears it."""

    def test_additional_information_per_language(self):
        english = self.template.with_context(lang="en_US")
        spanish = self.template.with_context(lang="es_ES")
        english.technical_features = TEXT
        spanish.technical_features = PLACEHOLDER
        with self.backend.work_on("woocommerce.product.template") as work:
            mapper = work.component(usage="export.mapper")
            self.assertEqual(
                mapper.additional_information(english),
                {"additional_information": TEXT_HEX},
            )
            self.assertEqual(
                mapper.additional_information(spanish),
                {"additional_information": None},
            )

    def test_no_value_reaches_the_meta_as_null(self):
        with self.backend.work_on("woocommerce.product.template") as work:
            adapter = work.component(usage="backend.adapter")
            data = {"additional_information": None}
            adapter._format_data(data)
        self.assertEqual(
            data, {"meta_data": [{"key": "additional_information", "value": None}]}
        )
