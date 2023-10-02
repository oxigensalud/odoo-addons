# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    company_id = fields.Many2one(default=lambda r: False)
    customer_id = fields.Many2one(compute="_compute_customer", store=True)

    @api.depends("equipment_id")
    def _compute_customer(self):
        for record in self:
            record.customer_id = record.equipment_id.customer_id
