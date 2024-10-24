# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    name = fields.Char(translate=False)
    stock_location_id = fields.Many2one("stock.location", string="Stock Location")
    company_id = fields.Many2one(default=lambda r: False)
    my_team_equipment = fields.Boolean(
        search="_search_my_team_equipment", compute="_compute_my_team_equipment"
    )
    # Specific fields only for IT
    operating_system_id = fields.Many2one(
        "maintenance.equipment.operating.system",
        groups="oxigen_maintenance.group_maintenance_it",
        tracking=True,
    )
    phone_imei_1 = fields.Char(
        groups="oxigen_maintenance.group_maintenance_it", tracking=True, string="IMEI 1"
    )
    phone_imei_2 = fields.Char(
        groups="oxigen_maintenance.group_maintenance_it", tracking=True, string="IMEI 2"
    )
    phone_pin = fields.Char(
        groups="oxigen_maintenance.group_maintenance_it", tracking=True, string="PIN"
    )
    phone_puk = fields.Char(
        groups="oxigen_maintenance.group_maintenance_it", tracking=True, string="PUK"
    )
    phone_line = fields.Char(
        groups="oxigen_maintenance.group_maintenance_it",
        tracking=True,
        string="Phone Line",
    )
    phone_extension = fields.Char(
        groups="oxigen_maintenance.group_maintenance_it",
        tracking=True,
        string="Extension",
    )
    phone_active_pin = fields.Boolean(
        groups="oxigen_maintenance.group_maintenance_it",
        tracking=True,
        string="Active PIN",
    )
    phone_icc_code = fields.Char(
        groups="oxigen_maintenance.group_maintenance_it",
        tracking=True,
        string="ICC Code",
    )
    maintenance_team_id = fields.Many2one(tracking=True)
    category_id = fields.Many2one(tracking=True)
    model = fields.Char(tracking=True)
    name = fields.Char(tracking=True)
    partner_id = fields.Many2one(check_company=False)

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

    equipment_assign_to = fields.Selection(
        selection_add=[("customer", "Customer")], ondelete={"customer": "set default"}
    )
    customer_id = fields.Many2one("res.partner")

    def _prepare_request_from_plan(self, maintenance_plan, next_maintenance_date):

        res = super(MaintenanceEquipment, self)._prepare_request_from_plan(
            maintenance_plan, next_maintenance_date
        )
        kind = maintenance_plan.maintenance_kind_id.name or _("Unspecified kind")
        res["name"] = _("%s - %s - %s") % (kind, self.name, maintenance_plan.name)

        if maintenance_plan.employee_id:
            res["employee_id"] = maintenance_plan.employee_id.id

        return res
