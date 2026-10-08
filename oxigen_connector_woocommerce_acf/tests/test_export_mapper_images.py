# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from io import BytesIO

from PIL import Image

from odoo.addons.component.tests.common import SavepointComponentCase

VIDEO_URL = "https://www.youtube.com/watch?v=aaaaaaaaaaa"


class TestExportMapperImages(SavepointComponentCase):
    """The images the template export sends leave out the gallery images of
    its videos, and only them."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.backend = cls.env["woocommerce.backend"].create(
            {
                "name": "WooCommerce test backend",
                "url": "http://127.0.0.1:1",
                "consumer_key": "ck_test",
                "consumer_secret": "cs_test",
                # No export languages: with connector_woocommerce_wpml
                # installed, each of them needs a WPML code
                "language_id": cls.env.ref("base.lang_en").id,
                "client_order_ref_prefix": "WC",
            }
        )

    @staticmethod
    def _image_data(color):
        stream = BytesIO()
        Image.new("RGB", (8, 8), color).save(stream, format="PNG")
        return base64.b64encode(stream.getvalue())

    def _create_gallery_image(self, **values):
        return self.env["product.image"].create(
            {"name": "Gallery image", "image_1920": self._image_data("red"), **values}
        )

    def _image_attachment(self, record):
        return self.env["ir.attachment"].search(
            [
                ("res_model", "=", record._name),
                ("res_id", "=", record.id),
                ("res_field", "=", "image_1920"),
            ]
        )

    def _align_next_ids(self):
        """The next template and the next gallery image get the same id, above
        every id either sequence has given. A sequence is not rolled back:
        both stay ahead after the test."""
        self.env.cr.execute(
            """
            SELECT GREATEST(
                (SELECT last_value FROM product_template_id_seq),
                (SELECT last_value FROM product_image_id_seq)
            ) + 1
            """
        )
        next_id = self.env.cr.fetchone()[0]
        self.env.cr.execute(
            "SELECT setval('product_template_id_seq', %s, false)", (next_id,)
        )
        self.env.cr.execute(
            "SELECT setval('product_image_id_seq', %s, false)", (next_id,)
        )

    def _exported_attachments(self, template):
        with self.backend.work_on("woocommerce.product.template") as work:
            mapper = work.component(usage="export.mapper")
            return mapper._get_product_image_attachments(template).attachment_id

    def test_only_the_video_image_left_out_when_it_has_the_template_id(self):
        self.backend.use_main_product_image = "first"
        self._align_next_ids()
        template = self.env["product.template"].create(
            {"name": "Simple product", "image_1920": self._image_data("white")}
        )
        video = self._create_gallery_image(
            product_tmpl_id=template.id, video_url=VIDEO_URL
        )
        photo = self._create_gallery_image(product_tmpl_id=template.id)
        self.assertEqual(video.id, template.id)
        self.assertEqual(
            self._exported_attachments(template),
            self._image_attachment(template) | self._image_attachment(photo),
        )
