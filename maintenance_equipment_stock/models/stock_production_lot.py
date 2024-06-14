# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"

    equipment_ids = fields.One2many("maintenance.equipment", inverse_name="lot_id")

    def action_lot_open_equipment(self):
        self.ensure_one()
        return self.equipment_ids.get_formview_action()
