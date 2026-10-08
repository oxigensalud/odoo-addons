# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime, timedelta

from freezegun import freeze_time

from odoo.tests.common import SavepointCase


class TestProductExportMarking(SavepointCase):
    """A change to an ACF field the template export sends marks the variations
    of a variable product, which is exported through them. No backend is
    needed: the export date of a product is computed without one."""

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    def _create_variable_template(self):
        attribute = self.env["product.attribute"].create({"name": "Size"})
        values = self.env["product.attribute.value"].create(
            [
                {"name": "Small", "attribute_id": attribute.id},
                {"name": "Large", "attribute_id": attribute.id},
            ]
        )
        return self.env["product.template"].create(
            {
                "name": "Variable product",
                "woocommerce_enabled": True,
                "attribute_line_ids": [
                    (
                        0,
                        0,
                        {
                            "attribute_id": attribute.id,
                            "value_ids": [(6, 0, values.ids)],
                        },
                    ),
                ],
            }
        )

    def test_professional_product_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 0), datetime(2030, 1, 1, 12, 0, 0)],
        )
        self.clock.tick(timedelta(seconds=1))
        template.professional_product = True
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 1), datetime(2030, 1, 1, 12, 0, 1)],
        )

    def test_prescription_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 0), datetime(2030, 1, 1, 12, 0, 0)],
        )
        self.clock.tick(timedelta(seconds=1))
        template.medical_prescription_required = True
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 1), datetime(2030, 1, 1, 12, 0, 1)],
        )
