# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    lot_id = fields.Many2one(
        "stock.production.lot", readonly=True, copy=False, tracking=True
    )
    supplier_lot_number = fields.Char(
        compute="_compute_supplier_number",
        inverse="_inverse_supplier_lot_number",
        readonly=False,
        store=True,
    )
    supplier_product_id = fields.Many2one(
        "product.product",
        compute="_compute_supplier_product",
        inverse="_inverse_supplier_lot_number",
        domain=[
            ("type", "=", "product"),
            ("tracking", "=", "serial"),
            ("maintenance_lot", "=", True),
        ],
        readonly=False,
        tracking=True,
    )
    picking_id = fields.Many2one("stock.picking", readonly=True, copy=False)
    stock_move_line_id = fields.Many2one("stock.move.line", readonly=True, copy=False)
    purchase_id = fields.Many2one("purchase.order", readonly=True, copy=False)

    @api.depends("lot_id", "lot_id.name")
    def _compute_supplier_number(self):
        for record in self:
            record.supplier_lot_number = record.lot_id.name

    @api.depends("lot_id")
    def _compute_supplier_product(self):
        for record in self:
            record.supplier_product_id = record.lot_id.product_id

    def _inverse_supplier_lot_number(self):
        for record in self:
            if record.lot_id:
                record.lot_id.write(
                    {
                        "name": record.supplier_lot_number or record.lot_id.name,
                        "product_id": record.supplier_product_id.id
                        or record.lot_id.product_id.id,
                    }
                )
            elif record.supplier_lot_number and record.supplier_product_id:
                record.lot_id = self.env["stock.production.lot"].create(
                    {
                        "name": record.supplier_lot_number,
                        "product_id": record.supplier_product_id.id,
                    }
                )
