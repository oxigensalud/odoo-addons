# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    stock_location_id = fields.Many2one("stock.location", string="Location")
    my_team_equipment = fields.Boolean(
        search="_search_my_team_equipment", compute="_compute_my_team_equipment"
    )

    def _search_my_team_equipment(self, operator, value):
        if operator != "=" or not value:
            return []
        return [
            (
                "maintenance_team_id",
                "in",
                [False]
                + self.env["maintenance.team"]
                .search([("member_ids", "=", self.env.user.id)])
                ._get_parent_teams()
                .ids,
            )
        ]

    def _compute_my_team_equipment(self):
        for record in self:
            record.my_team_equipment = (
                not record.maintenance_team_id
                or record.maintenance_team_id
                in self.env["maintenance.team"]
                .search([("member_ids", "=", self.env.user.id)])
                ._get_parent_teams()
            )

    def _prepare_request_from_plan(self, maintenance_plan, next_maintenance_date):

        res = super(MaintenanceEquipment, self)._prepare_request_from_plan(
            maintenance_plan, next_maintenance_date
        )
        kind = maintenance_plan.maintenance_kind_id.name or _("Unspecified kind")
        res["name"] = _("%s - %s - %s") % (kind, self.name, maintenance_plan.name)

        if maintenance_plan.employee_id:
            res["employee_id"] = maintenance_plan.employee_id.id

        return res
