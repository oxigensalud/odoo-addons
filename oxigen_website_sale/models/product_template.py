# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    professional_product = fields.Boolean()
    medical_prescription_required = fields.Boolean(
        string="Product with medical prescription"
    )
