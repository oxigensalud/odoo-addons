# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    is_gas = fields.Boolean(compute="_compute_is_gas", store=True, readonly=False)

    @api.depends("product_variant_ids.onu_no")
    def _compute_is_gas(self):
        for product in self:
            onu_numbers = product.product_variant_ids.mapped("onu_no")
            if isinstance(onu_numbers, int):
                onu_numbers = [onu_numbers]
            product.is_gas = any(onu_numbers)


class ProductProduct(models.Model):
    _inherit = "product.product"

    onu_no = fields.Integer()
