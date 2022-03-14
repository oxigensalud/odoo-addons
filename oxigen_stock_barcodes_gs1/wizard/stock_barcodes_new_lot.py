# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class WizStockBarcodesNewLot(models.TransientModel):
    _inherit = "wiz.stock.barcodes.new.lot"

    # override string.
    expiration_date = fields.Datetime(string="Removal Date")

    def _prepare_lot_values(self):
        vals = super()._prepare_lot_values()
        if "expiration_date" in vals:
            # Oxigen wants the group 17 to be removal date.
            vals.update({"removal_date": self.expiration_date})
            vals.pop("expiration_date")
        return vals
