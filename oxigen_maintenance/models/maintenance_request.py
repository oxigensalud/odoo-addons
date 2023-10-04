# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    company_id = fields.Many2one(default=lambda r: False)
    customer_id = fields.Many2one(compute="_compute_customer", store=True)

    @api.depends("equipment_id")
    def _compute_customer(self):
        for record in self:
            record.customer_id = record.equipment_id.customer_id

    @api.onchange("maintenance_team_id")
    def _onchange_maintenance_team(self):
        if self.user_id not in self.maintenance_team_id.member_ids:
            self.user_id = False
