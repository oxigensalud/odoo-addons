# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, fields, models
from odoo.exceptions import ValidationError


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

    def write(self, vals):
        for rec in self:
            if rec.tracking == "serial" and "tracking" in vals:
                mrp_type = vals.get("mrp_type", rec.mrp_type)
                if vals["tracking"] != "serial" and mrp_type:
                    raise ValidationError(
                        _(
                            "You cannot change the tracking of the product,"
                            " if you have an assigned type mrp [%s]"
                        )
                        % mrp_type
                    )
        return super(ProductTemplate, self).write(vals)
