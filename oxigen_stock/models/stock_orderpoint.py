# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class StockOrderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _get_product_context(self, visibility_days=0):
        res = super()._get_product_context(visibility_days=visibility_days)
        # We want to consider all incoming/outgoing moves.
        res.pop("to_date")
        return res
