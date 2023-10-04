# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    maintenance_team_ids = fields.Many2many(
        "maintenance.team", "maintenance_team_users_rel", string="Maintenance Teams"
    )
