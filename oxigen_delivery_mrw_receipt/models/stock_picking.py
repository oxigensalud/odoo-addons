# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def action_open_immediate_mrw_wizard(self):
        self.ensure_one()
        view_id = self.env.ref(
            "oxigen_delivery_mrw_receipt.view_immediate_transfer_mrw_in"
        ).id
        ctx = self._context.copy()
        ctx["default_pick_ids"] = [(4, p.id) for p in self]
        ctx["default_immediate_transfer_line_ids"] = []
        return {
            "name": _("Create MRW Receipt"),
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "stock.immediate.transfer",
            "view_id": view_id,
            "views": [(view_id, "form")],
            "target": "new",
            "context": ctx,
        }

    def send_to_shipper(self):
        if self.sale_id:
            super().send_to_shipper()
        else:
            self.ensure_one()
            res = self.carrier_id.send_shipping(self)[0]
            if res["tracking_number"]:
                self.carrier_tracking_ref = res["tracking_number"]
            order_currency = self.company_id.currency_id
            msg = _(
                "Shipment sent to carrier %(carrier_name)s for shipping with tracking"
                " number %(ref)s<br/>Cost: %(price).2f %(currency)s",
                carrier_name=self.carrier_id.name,
                ref=self.carrier_tracking_ref,
                price=self.carrier_price,
                currency=order_currency.name,
            )
            self.message_post(body=msg)

    def pricelist_send_shipping(self, pickings):
        res = []
        for picking in pickings:
            carrier = picking.carrier_id
            sale = picking.sale_id
            price = carrier._pricelist_get_price(sale) if sale else 0.0
            res = res + [{"exact_price": price, "tracking_number": False}]
        return res
