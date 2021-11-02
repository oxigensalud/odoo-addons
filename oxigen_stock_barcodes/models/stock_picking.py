# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    # TODO: translations to spanish.

    def action_barcode_scan(self):
        self._prepare_stock_barcodes_sequence()
        action = super().action_barcode_scan()
        if self.picking_type_code != "incoming":
            # Ask to scan the source location
            ctx = action.get("context", {})
            ctx["default_message"] = _("Scan the Source Location")
            ctx["default_message_type"] = "info"
            action["context"] = ctx
        else:
            # Ask to scan a product/lot
            ctx = action.get("context", {})
            ctx["default_message"] = _("Scan a Product or Lot/Serial number")
            ctx["default_message_type"] = "info"
            ctx["default_location_src_scanned"] = True
            action["context"] = ctx
        return action

    def _prepare_stock_barcodes_sequence(self):
        # TODO: improve logic here to be more efficient guiding the operator...
        current_seq = 10
        for ml in self.move_line_ids.sorted(key=lambda r: r.location_id.name):
            ml.stock_barcodes_sequence = current_seq
            current_seq += 1
