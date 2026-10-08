# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.depends(
        # A variation is exported with its parent template, ACF fields included
        "product_tmpl_id.technical_features",
        "product_tmpl_id.product_template_image_ids",
        "product_tmpl_id.product_template_image_ids.video_url",
        "product_tmpl_id.product_template_image_ids.title",
    )
    def _compute_woocommerce_write_date(self):
        super()._compute_woocommerce_write_date()
