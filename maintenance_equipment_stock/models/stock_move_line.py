# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMoveLine(models.Model):

    _inherit = "stock.move.line"

    def _action_done(self):
        result = super()._action_done()
        for ml in self.filtered(lambda m: m.exists()):
            if (
                ml.product_id.maintenance_lot
                and ml.product_id.type == "product"
                and ml.product_id.tracking == "serial"
            ):
                ml._create_maintenance_equipment()
        return result

    def _create_maintenance_equipment(self):
        return self.env["maintenance.equipment"].create(
            self._create_maintenance_equipment_vals()
        )

    def _create_maintenance_equipment_vals(self):
        return {
            "lot_id": self.lot_id.id,
            "picking_id": self.move_id.picking_id.id,
            "stock_move_line_id": self.id,
            "name": self.product_id.display_name,
            # "company_id": self.company_id.id,
            "company_id": False,
            "partner_id": self.move_id.picking_id.partner_id.id,
            "category_id": self.product_id.maintenance_category_id.id,
            "maintenance_team_id": self.product_id.maintenance_team_id.id,
            "purchase_id": self.move_id.picking_id.purchase_id.id,
        }
