# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockNumberPackageValidateWiz(models.TransientModel):
    _inherit = "stock.number.package.validate.wizard"

    mrw_is_in_picking = fields.Boolean(
        compute="_compute_mrw_is_in_picking",
        readonly=False,
        store=True,
    )

    @api.depends("pick_ids")
    def _compute_mrw_is_in_picking(self):
        for wizard in self:
            wizard.mrw_is_in_picking = False
            if len(wizard.pick_ids) == 1:
                picking = wizard.pick_ids
                if picking.carrier_id and picking.carrier_id.delivery_type == "mrw":
                    wizard.mrw_is_in_picking = picking.picking_type_code == "incoming"

    def mrw_send_shipping(self):
        if self.pick_ids.picking_type_code == "incoming" and len(self.pick_ids) == 1:
            self.pick_ids.write({"number_of_packages": self.number_of_packages})
            return (
                self.pick_ids[0]
                .sudo()
                .with_context(mrw_is_in_picking=True)
                .send_to_shipper()
            )
        return super().mrw_send_shipping()
