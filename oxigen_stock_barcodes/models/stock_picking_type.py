# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockPickingType(models.Model):
    _inherit = "stock.picking.type"

    # TODO: add a pull_barcode_workflow option?
