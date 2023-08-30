# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import json

from odoo import api, fields, models

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
