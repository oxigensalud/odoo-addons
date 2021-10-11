# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class Orderpoint(models.Model):
    _inherit = "stock.warehouse.orderpoint"

    def _quantity_in_progress(self):
        # Consider also RFQ lines not linked explicity to an orderpoint.
        res = super()._quantity_in_progress()
        for rec in self:
            po_lines = self.env["purchase.order.line"].search(
                [
                    ("state", "in", ("draft", "sent", "to approve")),
                    ("orderpoint_id", "=", False),
                    ("product_id", "=", rec.product_id.id),
                    ("order_id.picking_type_id.warehouse_id", "=", rec.warehouse_id.id),
                ]
            )
            for poline in po_lines:
                res.setdefault(rec.id, 0)
                res[rec.id] += poline.product_uom._compute_quantity(
                    poline.product_qty, rec.product_uom, round=False
                )
        return res
