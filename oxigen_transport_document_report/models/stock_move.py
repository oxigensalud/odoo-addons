# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    adr_tag = fields.Selection(
        selection=[
            ("21", "2.1"),
            ("22", "2.2"),
            ("23", "2.3"),
            ("24", "2.4"),
            ("51", "2.2 (5.1)"),
        ],
        default="22",
    )
    tunel_code = fields.Selection(
        selection=[
            ("e", "E"),
            ("ce", "C/E"),
            ("bd", "B/D"),
            ("2bd", "2 (B/D)"),
        ],
        default="e",
    )
    transport_category = fields.Selection(
        selection=[
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
        ],
        default="3",
    )
    container_id = fields.Many2one(comodel_name="product.container")
    filled_weight = fields.Float(
        compute="_compute_filled_weight", store=True, readonly=False
    )
    total_weight = fields.Float(
        compute="_compute_total_weight", store=True, readonly=False
    )
    delivered_quantity = fields.Float(compute="_compute_delivered_quantity")
    onu_no = fields.Integer(related="product_id.onu_no")

    @api.depends(
        "container_id.void_weight",
        "container_id.liter_capacity",
        "product_id.weight",
        "product_id.volume",
    )
    def _compute_filled_weight(self):
        for move in self:
            move.filled_weight = (
                move.container_id.void_weight
                + move.container_id.liter_capacity
                * move.product_id.weight
                / (move.product_id.volume or 1.0)
            )

    @api.depends("product_uom_qty", "filled_weight")
    def _compute_total_weight(self):
        for move in self:
            move.total_weight = move.product_uom_qty * move.filled_weight

    @api.depends("product_uom_qty", "filled_weight", "container_id.void_weight")
    def _compute_delivered_quantity(self):
        for move in self:
            move.delivered_quantity = move.product_uom_qty * (
                move.filled_weight - move.container_id.void_weight
            )
