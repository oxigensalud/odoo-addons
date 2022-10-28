# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import _, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    def send_to_shipper(self):
        if self.env.context.get("mrw_is_in_picking", False) and not self.sale_id:
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
        else:
            super().send_to_shipper()

    def pricelist_send_shipping(self, pickings):
        res = super().pricelist_send_shipping()
        if self.env.context.get("mrw_is_in_picking", False):
            for picking in pickings:
                carrier = picking.carrier_id
                sale = picking.sale_id
                price = carrier._pricelist_get_price(sale) if sale else 0.0
                res = res + [{"exact_price": price, "tracking_number": False}]
        return res
