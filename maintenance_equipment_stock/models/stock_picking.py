# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockPicking(models.Model):

    _inherit = "stock.picking"

    maintenance_equipment_ids = fields.One2many(
        "maintenance.equipment", inverse_name="picking_id"
    )
    maintenance_equipment_count = fields.Integer(
        compute="_compute_maintenance_equipment_count"
    )

    def _compute_maintenance_equipment_count(self):
        for record in self:
            record.maintenance_equipment_count = len(record.maintenance_equipment_ids)

    def action_show_equipments(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "maintenance.hr_equipment_action"
        )
        action["context"] = {}
        action["domain"] = [("id", "in", self.maintenance_equipment_ids.ids)]
        return action
