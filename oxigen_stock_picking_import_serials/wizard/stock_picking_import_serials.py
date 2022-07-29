# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models


class StockPickingImportSerials(models.TransientModel):
    _inherit = "stock.picking.import.serials"

    def _prepare_additional_tracking_values(self, data, company):
        res = super()._prepare_additional_tracking_values(data, company)
        return {**res, **dict(zip(["nos", "dn"], data))}
