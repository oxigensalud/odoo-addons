# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends(
        # A variation is exported with its parent template, ACF fields included
        "product_tmpl_id.professional_product",
        "product_tmpl_id.medical_prescription_required",
        # and so are its images, except those with a video URL
        "product_tmpl_id.product_template_image_ids.video_url",
    )
    def _compute_woocommerce_write_date(self):
        super()._compute_woocommerce_write_date()
