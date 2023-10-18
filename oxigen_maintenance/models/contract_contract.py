# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ContractContract(models.Model):

    _inherit = "contract.contract"

    maintenance_plan_ids = fields.Many2many(
        comodel_name="maintenance.plan",
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

    @api.onchange("equipment_ids")
    def onchange_equipment_ids(self):
        plans = self.maintenance_plan_ids
        for plan in plans:
            if plan.equipment_id and plan.equipment_id.id not in self.equipment_ids.ids:
                self.maintenance_plan_ids -= plan

    def _action_show_maintenance_requests_domain(self):
        if self.maintenance_plan_ids:
            return [("maintenance_plan_id", "in", self.maintenance_plan_ids.ids)]
        return super()._action_show_maintenance_requests_domain()
