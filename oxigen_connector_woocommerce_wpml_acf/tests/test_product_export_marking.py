# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import timedelta
from io import BytesIO

from freezegun import freeze_time
from PIL import Image

from odoo.addons.connector_woocommerce_wpml.tests.common import WooCommerceWPMLCase

VIDEO_URL = "https://www.youtube.com/watch?v=aaaaaaaaaaa"
OTHER_VIDEO_URL = "https://www.youtube.com/watch?v=bbbbbbbbbbb"


class TestProductExportMarking(WooCommerceWPMLCase):
    """A change to a field the ACF template export reads marks the products
    that carry it: a simple product is exported as its template, a variable
    one through its variations."""

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

    # Simple products

    def test_videos_reordered_marks_simple_template(self):
        template = self._create_template("WooCommerce simple product")
        self._create_gallery_image(
            product_tmpl_id=template.id, video_url=VIDEO_URL, sequence=10
        )
        video = self._create_gallery_image(
            product_tmpl_id=template.id, video_url=OTHER_VIDEO_URL, sequence=20
        )
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        video.sequence = 5
        self.assert_touched(template)

    # Variable products

    def test_technical_features_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        template.technical_features = "<p>Technical features</p>"
        self.assert_touched(template.product_variant_ids)

    def test_video_added_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        self._create_gallery_image(product_tmpl_id=template.id, video_url=VIDEO_URL)
        self.assert_touched(template.product_variant_ids)

    def test_video_url_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        video = self._create_gallery_image(
            product_tmpl_id=template.id, video_url=VIDEO_URL
        )
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        video.video_url = OTHER_VIDEO_URL
        self.assert_touched(template.product_variant_ids)

    def test_video_description_change_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        video = self._create_gallery_image(
            product_tmpl_id=template.id, video_url=VIDEO_URL
        )
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        video.title = "Video description"
        self.assert_touched(template.product_variant_ids)

    def test_videos_reordered_marks_variants_of_variable_template(self):
        template = self._create_variable_template()
        self._create_gallery_image(
            product_tmpl_id=template.id, video_url=VIDEO_URL, sequence=10
        )
        video = self._create_gallery_image(
            product_tmpl_id=template.id, video_url=OTHER_VIDEO_URL, sequence=20
        )
        self._remember_write_dates(template)
        self.clock.tick(timedelta(seconds=1))
        video.sequence = 5
        self.assert_touched(template.product_variant_ids)
