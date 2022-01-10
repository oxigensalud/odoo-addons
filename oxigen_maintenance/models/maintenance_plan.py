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
