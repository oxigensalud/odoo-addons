# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    maintenance_plan_id = fields.Many2one(
        "maintenance.plan",
        string="Maintenance Plan",
        domain="[('equipment_id', 'in', equipment_ids)]",
    )
    maintenance_plan_visible = fields.Boolean(
        compute="_compute_maintenance_plan_visible"
    )

    @api.depends("equipment_ids")
    def _compute_maintenance_plan_visible(self):
        for rec in self:
            rec.maintenance_plan_visible = any(
                map(lambda x: x.maintenance_plan_ids, rec.equipment_ids)
            )
