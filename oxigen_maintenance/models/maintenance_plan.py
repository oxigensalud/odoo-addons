# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class MaintenancePlan(models.Model):
    _inherit = "maintenance.plan"

    @api.returns("self")
    def _default_employee_get(self):
        return self.env["hr.employee"].search([("user_id", "=", self.env.uid)], limit=1)

    employee_id = fields.Many2one(
        "hr.employee", string="Employee", default=_default_employee_get
    )

    contract_ids = fields.Many2many(
        comodel_name="contract.contract",
        string="Contracts",
    )
    contract_count = fields.Integer(
        compute="_compute_contract_count",
    )

    @api.depends("contract_ids")
    def _compute_contract_count(self):
        for record in self:
            record.contract_count = len(record.contract_ids.ids)

    def action_view_contracts(self):
        action = self.env.ref("contract.action_customer_contract").sudo().read()[0]
        if len(self.contract_ids) > 1:
            action["domain"] = [("id", "in", self.contract_ids.ids)]
        elif self.contract_ids:
            action["views"] = [
                (self.env.ref("contract.contract_contract_form_view").id, "form")
            ]
            action["res_id"] = self.contract_ids.id
        action["context"] = {
            "default_maintenance_plan_ids": self.ids,
            "is_contract": 1,
            "search_default_not_finished": 1,
            "search_default_recurring_invoices": 1,
            "default_recurring_invoices": 1,
            "default_contract_type": "purchase",
        }
        return action
