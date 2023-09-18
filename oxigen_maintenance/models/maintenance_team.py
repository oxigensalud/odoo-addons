# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class MaintenanceTeam(models.Model):
    _inherit = "maintenance.team"

    def _get_parent_teams(self):
        if not self:
            return self
        return self | self.mapped("parent_id")._get_parent_teams()
