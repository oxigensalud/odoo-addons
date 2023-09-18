# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    lot_id = fields.Many2one("stock.production.lot", readonly=True)
    picking_id = fields.Many2one("stock.picking", readonly=True)
    stock_move_line_id = fields.Many2one("stock.move.line", readonly=True)
    purchase_id = fields.Many2one("purchase.order", readonly=True)
