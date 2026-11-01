# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class MaintenanceTeam(models.Model):
    _inherit = "maintenance.team"

    company_id = fields.Many2one(default=lambda r: False)

    def _get_parent_teams(self):
        if not self:
            return self
        return self | self.mapped("parent_id")._get_parent_teams()
