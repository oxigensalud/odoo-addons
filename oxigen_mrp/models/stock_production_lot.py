# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.base_sparse_field.models.fields import Serialized


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    @api.model
    def _get_product_mrp_workflow(self):
        return {
            "cylinder": {
                "manufacturer",
                "weight",
                "manufacture_date",
                "retesting_date",
                "next_retesting_date",
            },
            "valve": {"manufacturer", "manufacture_date", "removal_date"},
            "empty_cylinder": {
                "manufacturer",
                "manufacture_date",
                "retesting_date",
                "next_retesting_date",
            },
        }

    @api.model
    def get_all_product_mrp_fields(self):
        all_product_mrp_fields = set()
        for mrp_fields in self._get_product_mrp_workflow().values():
            all_product_mrp_fields |= mrp_fields
        return all_product_mrp_fields

    manufacturer = fields.Many2one(
        comodel_name="res.partner",
    )
    weight = fields.Float()
    manufacture_date = fields.Date()
    retesting_date = fields.Date()
    next_retesting_date = fields.Date()

    mrp_fields_allowed = Serialized(compute="_compute_mrp_fields_allowed")

    @api.depends("product_id.mrp_type")
    def _compute_mrp_fields_allowed(self):
        allowed_fields = self._get_product_mrp_workflow()
        for rec in self:
            rec.mrp_fields_allowed = list(
                allowed_fields.get(rec.product_id.mrp_type, set())
            )

    # TODO: write and create methods to check the fields allowed and/or
    # constraints to check the fields allowed

    @api.constrains(
        "manufacturer",
        "weight",
        "manufacture_date",
        "retesting_date",
        "next_retesting_date",
        "removal_date",
    )
    def _check_mrp_lot(self):
        for rec in self:
            if not rec.product_id.mrp_type and any(
                [rec[field] for field in rec.get_all_product_mrp_fields()]
            ):
                raise ValidationError(
                    _("The product %s has not a type (MRP) defined")
                    % rec.product_id.display_name
                )
            if (
                rec.removal_date
                and not rec.product_id.use_expiration_date
                and rec.product_id.mrp_type
                and rec.product_id.mrp_type != "valve"
            ):
                raise ValidationError(
                    _(
                        "The product %s is not a valve and has not expiration date"
                        % rec.product_id.display_name
                    )
                )
            if rec.product_id.mrp_type:
                not_allowed_fields = (
                    self.get_all_product_mrp_fields()
                    - self._get_product_mrp_workflow().get(
                        rec.product_id.mrp_type, set()
                    )
                )
                for field in not_allowed_fields:
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
