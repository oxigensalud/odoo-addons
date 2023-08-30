# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mrp_type = fields.Selection(
        string="Type (MRP)",
        selection=[
            ("cylinder", "Cylinder"),
            ("valve", "Valve"),
            ("empty_cylinder", "Empty Cylinder"),
        ],
    )
