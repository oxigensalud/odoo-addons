# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    # WARNING: override standard method, combines `wiz.stock.barcodes.read orignal`
    # and super at `wiz.stock.barcodes.read.picking`; both at `stock_barcodes`
    # module.
    def action_product_scaned_post(self, product):
        self.package_id = False
        if self.product_id != product and self.lot_id.product_id != product:
            self.lot_id = False
        self.product_id = product
        self.product_uom_id = self.product_id.uom_id
        self.packaging_id = self.product_id.packaging_ids[:1]
        # START OF CHANGES
        if not (self.manual_entry or self.is_manual_qty):
            # Do not override qty always, we are increasing it with lot scans.
            # See `oxigen_stock_barcodes_gs1` module and `process_lot` method.
            self.product_qty = 1.0
        # END OF CHANGES
        # Super in wiz.stock.barcodes.read.picking
        if self.auto_lot and self.picking_type_code != "incoming":
            self.get_lot_by_removal_strategy()
