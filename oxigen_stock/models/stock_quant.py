# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.tools import float_compare


class StockQuant(models.Model):
    _inherit = "stock.quant"

    def _gather(
        self,
        product_id,
        location_id,
        lot_id=None,
        package_id=None,
        owner_id=None,
        strict=False,
        qty=0,
    ):
        quants = super()._gather(
            product_id,
            location_id,
            lot_id=lot_id,
            package_id=package_id,
            owner_id=owner_id,
            strict=strict,
            qty=qty,
        )
        # Adjust reservation to be first FIFO/FEFO and then use location name
        # alphabetically
        removal_strategy = self._get_removal_strategy(product_id, location_id)
        if removal_strategy == "fifo":
            quants = quants.sorted(lambda q: (q.in_date, q.location_id.name))
        elif removal_strategy == "fefo":
            # It can happen that for some reason a quant does not have a removal_date
            # (expiry not stored at the beginning, past version issues...)
            quants_no_removal_date = quants.filtered(lambda q: not q.removal_date)
            quants_removal_date = quants.filtered(lambda q: q.removal_date)
            quants = quants_removal_date.sorted(
                lambda q: (q.removal_date, q.in_date, q.location_id.name)
            )
            quants |= quants_no_removal_date.sorted(
                lambda q: (q.in_date, q.location_id.name)
            )
        elif removal_strategy == "lifo":
            # sorting 2 keys and only one of them reversed it is a bit tricky,
            # Oxigen does not use this method at the moment, therefore it is
            # not worth implementing.
            pass
        return quants

    def action_apply_inventory(self):
        if not self.exists():
            return super().action_apply_inventory()

        if self.env.user.has_group("stock.group_stock_manager"):
            return super().action_apply_inventory()

        self.ensure_one()

        inventory_quants = self.filtered(
            lambda quant: quant.product_id.tracking in ["lot", "serial"]
            and not quant.lot_id
            and quant.inventory_diff_quantity != 0
        )

        serial_quants = self.filtered(
            lambda quant: float_compare(
                quant.inventory_quantity,
                1,
                precision_rounding=quant.product_uom_id.rounding,
            )
            > 0
            and quant.product_id.tracking == "serial"
            and quant.lot_id
        )

        if inventory_quants and not serial_quants:
            wiz_lines = [
                (0, 0, {"product_id": product.id, "tracking": product.tracking})
                for product in inventory_quants.mapped("product_id")
            ]
            wiz = self.env["stock.track.confirmation"].create(
                {"quant_ids": [(6, 0, self.ids)], "tracking_line_ids": wiz_lines}
            )
            return {
                "name": _("Tracked Products in Inventory Adjustment"),
                "type": "ir.actions.act_window",
                "view_mode": "form",
                "views": [(False, "form")],
                "res_model": "stock.track.confirmation",
                "target": "new",
                "res_id": wiz.id,
            }

        return super().action_apply_inventory()
