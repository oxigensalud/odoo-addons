# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class StockLocation(models.Model):
    _inherit = "stock.location"

    equipment_ids = fields.One2many(
        comodel_name="maintenance.equipment",
        inverse_name="location_id",
        string="Maintenance Equipment",
    )

    def action_view_equipment(self):
        result = self.env["ir.actions.act_window"]._for_xml_id(
            "maintenance.hr_equipment_action"
        )
        equipment_ids = self.equipment_ids.ids

        if len(equipment_ids) != 1:
            result["domain"] = [("id", "in", equipment_ids)]
        else:
            res = self.env.ref("maintenance.hr_equipment_view_form", False)
            result["views"] = [(res and res.id or False, "form")]
            result["res_id"] = equipment_ids[0]
        return result
