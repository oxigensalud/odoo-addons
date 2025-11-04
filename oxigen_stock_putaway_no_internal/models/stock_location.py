# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockLocation(models.Model):
    _inherit = "stock.location"

    def _excluded_location_usages(self):
        return ["internal"]

    def _get_putaway_strategy(
        self,
        product,
        quantity=0,
        package=None,
        packaging=None,
        additional_qty=None,
    ):
        putaway_location = super()._get_putaway_strategy(
            product,
            quantity=quantity,
            package=package,
            packaging=packaging,
            additional_qty=additional_qty,
        )
        if self.usage in self._excluded_location_usages():
            return putaway_location.location_id
        return putaway_location
