# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models


class StockPicking(models.Model):
    _inherit = "stock.move.line"

    stock_barcodes_sequence = fields.Integer(
        default=10, help="Technical field to order operations on barcode scanner",
    )
