# Copyright (C) 2021 ForgeFlow S.L.
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html)
import logging

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPickingInfo(models.TransientModel):
    _inherit = "wiz.candidate.picking"
    _description = "Add next remaining line to scan info in picking wizard"

    next_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        compute="_compute_first_move_line",
        readonly=True,
    )

    next_location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination location",
        compute="_compute_first_move_line",
        readonly=True,
    )

    next_location_source_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source",
        compute="_compute_first_move_line",
        readonly=True,
    )

    next_product_uom_qty = fields.Float(
        string="Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_first_move_line",
        readonly=True,
    )

    product_done_qty = fields.Float(
        string="Done Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_first_move_line",
        readonly=True,
    )

    @api.depends("scan_count", "picking_id")
    def _compute_first_move_line(self):
        for candidate in self:
            for move in candidate.picking_id.move_lines:
                if move.quantity_done <= move.product_uom_qty:
                    candidate.next_product_id = move.product_id
                    candidate.next_location_dest_id = move.location_dest_id
                    candidate.next_location_source_id = move.location_id
                    candidate.next_product_uom_qty = move.product_uom_qty
                    candidate.product_done_qty = move.quantity_done
                    break
