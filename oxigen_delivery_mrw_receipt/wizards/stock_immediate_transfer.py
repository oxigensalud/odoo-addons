# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, fields, models
from odoo.exceptions import UserError


class StockImmediateTransfer(models.TransientModel):
    _inherit = "stock.immediate.transfer"

    mrw_is_in_picking = fields.Boolean()

    def default_get(self, fields):
        res = super().default_get(fields)
        immediate_line = res.get("immediate_transfer_line_ids", False)
        if immediate_line and len(immediate_line) == 1:
            picking = self.env["stock.picking"].browse(
                immediate_line[0][2]["picking_id"]
            )
            if picking.carrier_id.delivery_type == "mrw":
                res["mrw_is_in_picking"] = picking.picking_type_code == "incoming"
                if picking.picking_type_code == "incoming":
                    sending_partner = picking.partner_id
                    receiving_partner = (
                        picking.location_dest_id.get_warehouse().partner_id
                    )
                    sending_mrw_address = picking.carrier_id.mrw_address(
                        sending_partner, picking.carrier_id.international_shipping
                    )
                    receving_mrw_address = picking.carrier_id.mrw_address(
                        receiving_partner, picking.carrier_id.international_shipping
                    )
                    res["mrw_to_address"] = (
                        "<u><b>PickUp Location</b></u>: <br>"
                        + self._prepare_html_address(sending_mrw_address)
                        + "<br>"
                        + "<u><b>Destination Location</b></u>:<br>"
                        + self._prepare_html_address(receving_mrw_address)
                    )
        return res

    def mrw_send_shipping(self):
        if len(self.pick_ids) > 1:
            raise UserError(_("You cannot create more than one MRW pick up at a time"))
        self.pick_ids[0].sudo().send_to_shipper()
