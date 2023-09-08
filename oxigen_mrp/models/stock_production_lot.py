# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base_sparse_field.models.fields import Serialized


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    def _get_product_mrp_workflow(self):
        return {
            "cylinder": {
                "manufacturer",
                "weight",
                "manufacture_date",
                "retesting_date",
                "next_retesting_date",
            },
            "valve": {"manufacturer", "manufacture_date", "valid_until_date"},
            "empty_cylinder": {
                "manufacturer",
                "manufacture_date",
                "retesting_date",
                "next_retesting_date",
            },
        }

    manufacturer = fields.Many2one(
        comodel_name="res.partner",
    )
    weight = fields.Float()
    manufacture_date = fields.Date()
    retesting_date = fields.Date()
    next_retesting_date = fields.Date()
    valid_until_date = fields.Date()

    mrp_fields_allowed = Serialized(compute="_compute_mrp_fields_allowed")

    @api.depends("product_id")
    def _compute_mrp_fields_allowed(self):
        allowed_fields = self._get_product_mrp_workflow()
        for rec in self:
            rec.mrp_fields_allowed = json.dumps(
                list(allowed_fields.get(rec.product_id.mrp_type, set()))
            )

    # TODO: write and create methods to check the fields allowed and/or
    # constraints to check the fields allowed

    @api.constrains(
        "manufacturer",
        "weight",
        "manufacture_date",
        "retesting_date",
        "next_retesting_date",
        "valid_until_date",
    )
    def _check_mrp_lot(self):
        for rec in self:
            if not rec.product_id.mrp_type:
                raise ValidationError(
                    _("The product %s has not a type (MRP) defined")
                    % rec.product_id.display_name
                )
            if rec.product_id.mrp_type:
                original_fields = rec._get_product_mrp_workflow()
                allowed_fields = original_fields[rec.product_id.mrp_type]
                diff_fields = set()
                for key, value in original_fields.items():
                    if key != rec.product_id.mrp_type:
                        diff_fields.update(value - allowed_fields)
                for field in diff_fields:
                    if rec[field]:
                        raise ValidationError(
                            _(
                                "The field %s is not allowed for the product"
                                " %s in the type MRP %s"
                                % (
                                    field,
                                    rec.product_id.display_name,
                                    rec.product_id.mrp_type,
                                )
                            )
                        )
