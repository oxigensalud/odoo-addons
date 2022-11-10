# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero


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

    def _process_stock_move_line(self):
        move_lines_dic = super()._process_stock_move_line()
        if (
            not self.option_group_id.get_option_value("lot_id", "forced")
            and self.picking_type_code != "incoming"
            and self.lot_id
        ):
            # update lot reserved
            lines = self.env["stock.move.line"].browse(list(move_lines_dic.keys()))
            for line in lines:
                move = line.move_id
                domain = [
                    ("location_id", "=", line.location_id.id),
                    ("product_id", "=", move.product_id.id),
                    ("lot_id", "=", line.lot_id.id),
                ]
                quant_to_reserve = self.env["stock.quant"].search(domain)
                smls = self.env["stock.move.line"].search(
                    [("move_id", "=", move.id), ("id", "!=", line.id)]
                )
                product_qty = self.product_uom_id._compute_quantity(
                    self.product_qty, line.product_id.uom_id
                )
                if (
                    float_compare(
                        quant_to_reserve.quantity,
                        product_qty,
                        line.product_id.uom_id.rounding,
                    )
                    >= 0
                ):
                    line.write({"product_uom_qty": line.product_uom_qty + product_qty})
                else:
                    raise UserError(_("No available units for this lot"))
                to_unreserve = product_qty
                for sml in smls:
                    if (
                        float_compare(
                            to_unreserve,
                            sml.product_uom_qty,
                            precision_rounding=sml.product_id.uom_id.rounding,
                        )
                        <= 0
                    ):
                        sml_qty_done = self.product_uom_id._compute_quantity(
                            sml.qty_done, line.product_id.uom_id
                        )
                        unreserve = min(
                            to_unreserve, sml.product_uom_qty - sml_qty_done
                        )
                        sml.write({"product_uom_qty": sml.product_uom_qty - unreserve})
                        to_unreserve -= unreserve
                    if float_is_zero(
                        to_unreserve, precision_rounding=line.product_id.uom_id.rounding
                    ):
                        break
            self.fill_todo_records()
        return move_lines_dic

    def create_new_stock_move_line(self, moves_todo, available_qty):
        # Avoid create a new stock move line if one already exists with same info
        if (
            not self.option_group_id.get_option_value("lot_id", "forced")
            and self.picking_type_code != "incoming"
            and self.lot_id
        ):
            existing = self.env["stock.move.line"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("lot_id", "=", self.lot_id.id),
                    ("location_id", "=", self.location_id.id),
                    ("move_id", "=", moves_todo[:1].id),
                ]
            )
            if existing:
                existing.write({"qty_done": existing.qty_done + available_qty})
                return existing
        return super().create_new_stock_move_line(moves_todo, available_qty)
