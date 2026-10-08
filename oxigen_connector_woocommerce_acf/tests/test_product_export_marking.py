# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime, timedelta
from io import BytesIO

from freezegun import freeze_time
from PIL import Image

from odoo.tests.common import SavepointCase

VIDEO_URL = "https://www.youtube.com/watch?v=aaaaaaaaaaa"


class TestProductExportMarking(SavepointCase):
    """A change to a field the ACF template export reads marks the products
    that carry it: a simple product is exported as its template, a variable
    one through its variations. No backend is needed: the export date of a
    product is computed without one."""

    def setUp(self):
        super().setUp()
        freezer = freeze_time("2030-01-01 12:00:00")
        self.clock = freezer.start()
        self.addCleanup(freezer.stop)

    @staticmethod
    def _image_data(color):
        stream = BytesIO()
        Image.new("RGB", (8, 8), color).save(stream, format="PNG")
        return base64.b64encode(stream.getvalue())

    def _create_gallery_image(self, **values):
        return self.env["product.image"].create(
            {"name": "Gallery image", "image_1920": self._image_data("red"), **values}
        )

    def _create_simple_template(self):
        return self.env["product.template"].create(
            {"name": "Simple product", "woocommerce_enabled": True}
        )

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

    # Simple products

    def test_video_url_set_marks_simple_template(self):
        template = self._create_simple_template()
        image = self._create_gallery_image(product_tmpl_id=template.id)
        self.assertEqual(
            template.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 0)
        )
        self.clock.tick(timedelta(seconds=1))
        image.video_url = VIDEO_URL
        self.assertEqual(
            template.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    def test_video_url_cleared_marks_simple_template(self):
        template = self._create_simple_template()
        image = self._create_gallery_image(
            product_tmpl_id=template.id, video_url=VIDEO_URL
        )
        self.assertEqual(
            template.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 0)
        )
        self.clock.tick(timedelta(seconds=1))
        image.video_url = False
        self.assertEqual(
            template.woocommerce_write_date, datetime(2030, 1, 1, 12, 0, 1)
        )

    # Variable products

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

    def test_video_url_set_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        image = self._create_gallery_image(product_tmpl_id=template.id)
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 0), datetime(2030, 1, 1, 12, 0, 0)],
        )
        self.clock.tick(timedelta(seconds=1))
        image.video_url = VIDEO_URL
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 1), datetime(2030, 1, 1, 12, 0, 1)],
        )

    def test_video_url_cleared_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        image = self._create_gallery_image(
            product_tmpl_id=template.id, video_url=VIDEO_URL
        )
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 0), datetime(2030, 1, 1, 12, 0, 0)],
        )
        self.clock.tick(timedelta(seconds=1))
        image.video_url = False
        self.assertEqual(
            template.product_variant_ids.mapped("woocommerce_write_date"),
            [datetime(2030, 1, 1, 12, 0, 1), datetime(2030, 1, 1, 12, 0, 1)],
        )
