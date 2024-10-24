# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    @api.depends(
        "professional_product",
        "medical_prescription_required",
    )
    def _compute_woocommerce_write_date(self):
        super()._compute_woocommerce_write_date()
