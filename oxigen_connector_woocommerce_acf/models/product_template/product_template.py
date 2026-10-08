# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends(
        "professional_product",
        "medical_prescription_required",
        # Gallery images with a video URL are left out of the exported images
        "product_template_image_ids.video_url",
    )
    def _compute_woocommerce_write_date(self):
        super()._compute_woocommerce_write_date()
