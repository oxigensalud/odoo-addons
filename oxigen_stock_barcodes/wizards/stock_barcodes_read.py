# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def _prepare_lot_domain(self):
        lot = self.env["stock.production.lot"]
        nos_size = lot.fields_get("nos", "size")["nos"]["size"]
        if len(self.barcode) == nos_size:
            domain = [
                ("nos", "=", self.barcode),
                ("product_id.nos_enabled", "=", True),
                ("nos_unknown", "=", False),
            ]
            if self.product_id:
                domain.append(("product_id", "=", self.product_id.id))
            lot = self.env["stock.production.lot"].search(domain)
        if not lot:
            domain = super()._prepare_lot_domain()
        return domain

    def open_actions(self):
        super().open_actions()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "stock.stock_picking_type_action"
        )
        return action
