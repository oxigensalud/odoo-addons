# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import _, api, fields, models
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

    @api.constrains("mrp_type")
    def _check_mrp_type(self):
        for rec in self:
            if rec.mrp_type not in (False, "valve") and rec.use_expiration_date:
                raise ValidationError(
                    _("Expiration date is not allowed for this type (MRP)")
                )

    def write(self, vals):
        for rec in self:
            if (
                "tracking" in vals
                and rec.tracking == "serial"
                and vals["tracking"] != rec.tracking
                and vals.get("mrp_type", rec.mrp_type)
            ):
                raise ValidationError(
                    _(
                        "You cannot change the tracking of the product,"
                        " if you have an assigned type (MRP)"
                    )
                )
            if "mrp_type" in vals and vals["mrp_type"] != rec.mrp_type:
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
