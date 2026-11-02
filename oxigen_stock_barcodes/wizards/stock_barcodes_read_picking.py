# Copyright 2022 ForgeFlow S.L.
# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    do_show_action_confirm = fields.Boolean(compute="_compute_do_show_action_confirm")

    @api.depends("picking_id", "picking_id.move_ids")
    def _compute_do_show_action_confirm(self):
        for rec in self:
            options = rec.option_group_id
            picking = rec.picking_id
            if (
                picking
                and picking.move_ids
                and picking.state == "draft"
                and options
                and options.barcode_guided_mode != "guided"
            ):
                rec.do_show_action_confirm = True
            else:
                rec.do_show_action_confirm = False

    def action_confirm_picking(self):
        self.ensure_one()
        if self.picking_id:
            self.picking_id.action_confirm()
            for move_line in self.picking_id.move_line_ids:
                if move_line.quantity > 0:
                    move_line.qty_picked = move_line.quantity
        return self.action_validate_picking()

    def action_product_scaned_post(self, product):
        res = super().action_product_scaned_post(product)
        self.packaging_id = self.product_id.packaging_ids[:1]
        # Do not override qty always, we are increasing it with lot scans.
        # See `oxigen_stock_barcodes_gs1` module and `process_lot` method.
        if not (self.manual_entry or self.is_manual_qty):
            self.product_qty = 1.0
        return res
