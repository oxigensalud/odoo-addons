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
            if "mrp_type" in vals:
                lots = self.env["stock.production.lot"].search(
                    [("product_id.product_tmpl_id", "=", rec.id)]
                )
                for lot in lots:
                    mrp_fields = lot._get_product_mrp_workflow().get(
                        rec.mrp_type, set()
                    )
                    if any([lot[field] for field in mrp_fields]):
                        raise ValidationError(
                            _(
                                "You cannot change the tracking of the product,"
                                " if you have fields with values in the lot"
                                " related to this type (MRP) [%s]"
                            )
                            % rec.mrp_type
                        )
        return super(ProductTemplate, self).write(vals)
