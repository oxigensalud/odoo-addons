# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

SEQUENCE_FORCE_OPERATION = 1
SEQUENCE_DO_NOT_DISPLAY = 999999


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    next_move_line_id = fields.Many2one(
        comodel_name="stock.move.line",
        string="Next Operation",
        compute="_compute_next_operation",
    )
    next_location_src_id = fields.Many2one(
        comodel_name="stock.location",
        string="Source Location",
        compute="_compute_next_operation",
    )
    next_location_dest_id = fields.Many2one(
        comodel_name="stock.location",
        string="Destination Location",
        compute="_compute_next_operation",
    )
    next_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        compute="_compute_next_operation",
    )
    next_lot_id = fields.Many2one(
        comodel_name="stock.production.lot",
        string="Lot/Serial Number",
        compute="_compute_next_operation",
    )
    next_product_uom_qty = fields.Float(
        string="Reserved Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_next_operation",
    )
    next_product_done_qty = fields.Float(
        string="Done Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        compute="_compute_next_operation",
    )
    location_src_scanned = fields.Boolean()
    location_dest_scanned = fields.Boolean()
    product_and_lot_scanned = fields.Boolean()
    message_type = fields.Selection(
        selection_add=[("location_no_match", "Incorrect Location")]
    )
    show_button_mark_location_dest = fields.Boolean(
        compute="_compute_show_button_mark_location_dest",
    )

    @api.depends(
        "picking_id",
        "picking_id.move_lines.quantity_done",
        "product_qty",
        "product_and_lot_scanned",
        "scan_log_ids",
        "picking_id.move_line_ids.stock_barcodes_sequence",
        "confirmed_moves",
    )
    def _compute_next_operation(self):
        for rec in self:
            if rec.picking_id:
                move_lines = rec.picking_id.move_line_ids.filtered(
                    lambda ml: ml.state in self._states_move_allowed()
                )
                for ml in move_lines.sorted(key=lambda r: r.stock_barcodes_sequence):
                    if ml.stock_barcodes_sequence == SEQUENCE_DO_NOT_DISPLAY:
                        continue
                    if (
                        self._get_qty_done_next_move_line(ml) < ml.product_uom_qty
                        or ml.stock_barcodes_sequence == SEQUENCE_FORCE_OPERATION
                    ):
                        rec.next_move_line_id = ml
                        rec.next_product_id = ml.product_id
                        rec.next_location_src_id = ml.location_id
                        rec.next_location_dest_id = ml.location_dest_id
                        rec.next_product_uom_qty = ml.product_uom_qty
                        rec.next_product_done_qty = self._get_qty_done_next_move_line(
                            ml
                        )
                        rec.next_lot_id = ml.lot_id
                        return
            rec.next_product_id = False
            rec.next_location_src_id = False
            rec.next_location_dest_id = False
            rec.next_product_uom_qty = False
            rec.next_product_done_qty = False
            rec.next_lot_id = False

    @api.depends(
        "location_src_scanned",
        "product_and_lot_scanned",
        "location_dest_scanned",
        "next_location_dest_id",
    )
    def _compute_show_button_mark_location_dest(self):
        for rec in self:
            rec.show_button_mark_location_dest = (
                self.location_src_scanned
                and self.product_and_lot_scanned
                and not self.location_dest_scanned
                and self.next_location_dest_id
                and self.next_location_dest_id.usage != "internal"
            )

    def _get_qty_done_next_move_line(self, ml):
        if (
            ml.picking_id.picking_type_id.code == "incoming"
            and ml.product_id.tracking == "lot"
        ):
            move_lines = ml.picking_id.move_line_ids.filtered(
                lambda ml2: ml2.product_id == ml.product_id
                and ml2.qty_done > 0
                and ml2.product_uom_qty == 0
            )
            return ml.qty_done + sum(move_lines.mapped("qty_done"))
        return ml.qty_done

    def _can_complete_without_scanning_dest_location(self):
        return (
            self.next_location_dest_id.usage not in ["internal", "view"]
            and self.next_product_uom_qty
            - self.next_product_done_qty
            - self.product_qty
            == 0
        )

    def check_done_conditions(self):
        res = super().check_done_conditions()
        if not self.next_product_id:
            return res
        # TODO: picking type pull workflow setting...
        if (
            self.picking_type_code != "incoming"
            and self.next_location_src_id
            and not self.location_src_scanned
        ):
            self._set_messagge_info("info", _("Scan the Source Location"))
            return False
        if not self.product_and_lot_scanned:
            self._set_messagge_info("info", _("Scan a Product or Lot/Serial number"))
            return False
        if self.next_location_dest_id and not self.location_dest_scanned:
            self._set_messagge_info(
                "info", _("Scan more units or the Destination Location")
            )
            return False
        return res

    def _set_messagge_info(self, type, message):
        if type == "success" and message == _("Barcode read correctly"):
            # we want full control on when to post a success msg.
            return
        return super()._set_messagge_info(type, message)

    def _prepare_move_line_values(self, candidate_move, available_qty):
        res = super()._prepare_move_line_values(candidate_move, available_qty)
        # Standard module forces the purchase UoM, why? I don't know...
        res["product_uom_id"] = (
            candidate_move.product_uom.id or self.product_id.uom_id.id
        )
        return res

    def _pre_process_barcode(self, barcode):
        domain = self._barcode_domain(barcode)
        location = self.env["stock.location"].search(domain)
        product = self.env["product.product"].search(domain)
        lot = False
        if self.env.user.has_group("stock.group_production_lot"):
            lot_domain = [("name", "=", barcode)]
            if self.next_product_id:
                lot_domain.append(("product_id", "=", self.next_product_id.id))
            lot = self.env["stock.production.lot"].search(lot_domain)
        return location, product, lot, {"raw_barcode": barcode}

    def _process_barcode_01_source_loc(self, location):
        if location:
            if location == self.next_location_src_id:
                self.location_src_scanned = True
                self._set_messagge_info(
                    "info", _("Waiting product or Lot/Serial number")
                )
                return False
            else:
                self._set_messagge_info(
                    "location_no_match", _("Source Location does not match.")
                )
                return False
        self._set_messagge_info("not_found", _("No location found."))
        return False

    def _process_barcode_02_lot_and_product(self, product, lot):
        if self.env.user.has_group("stock.group_production_lot"):
            if self.picking_type_code != "incoming" and lot != self.next_lot_id:
                self._set_messagge_info(
                    "not_found", _("Lot/Serial Number does not match.")
                )
                return False
            if len(lot) == 1:
                self.product_id = lot.product_id
            if lot:
                self.product_and_lot_scanned = True
                self.action_lot_scaned_post(lot)
                # Skip scan of dest location in some situations:
                if self._can_complete_without_scanning_dest_location():
                    return self._mark_location_dest_done()
                res = self.action_done()
                return res

        if product:
            if product == self.next_product_id:
                if product.tracking != "none" and self.picking_type_code != "incoming":
                    self._set_messagge_info(
                        "info", _("Please, scan the Lot/Serial number.")
                    )
                    return False
                elif product.tracking == "none":
                    self.product_and_lot_scanned = True
                    self.product_qty = 1
                else:
                    self.product_id = product
                    self._set_messagge_info(
                        "not_found",
                        _("Please, scan the Lot/Serial number or create it."),
                    )
                    return False
            else:
                self._set_messagge_info("not_found", _("Product does not match."))
                return False
        else:
            self._set_messagge_info("not_found", _("No product found."))
            return False

    def _process_barcode_03_dest_loc(self, location, product, lot, extra_data):
        if self.next_product_id == product or (
            self.next_lot_id and self.next_lot_id == lot
        ):
            if self.next_product_id.tracking != "serial":
                if (
                    self.product_qty + 1
                    > self.next_product_uom_qty - self.next_product_done_qty
                ):
                    self._set_messagge_info(
                        "not_found", _("You cannot add more quantity.")
                    )
                    return False
                self.product_qty += 1
                # Skip scan of dest location in some situations:
                if self._can_complete_without_scanning_dest_location():
                    return self._mark_location_dest_done()

            self._set_messagge_info(
                "info",
                _(
                    "Qty increased. Scan more products to increase quantity or "
                    "the destination location to finish the operation."
                ),
            )
            return False
        raw_barcode = extra_data.get("raw_barcode", "")
        if (
            raw_barcode == "OXIBARCODES00LOCDEST"
            and self.show_button_mark_location_dest
        ):
            return self._mark_location_dest_done()
        if location:
            if location == self.next_location_dest_id:
                return self._mark_location_dest_done(location=location)
            else:
                self._set_messagge_info(
                    "location_no_match", _("Destination Location does not match.")
                )
                return False
        else:
            self._set_messagge_info("not_found", _("No location found."))
            return False

    def _should_skip_scan_source_location(self):
        return (
            self.picking_type_code == "incoming"
            or self.next_location_src_id.usage == "transit"
        )

    def _mark_location_dest_done(self, location=False):
        self.location_dest_scanned = True
        self.location_id = location or self.next_location_dest_id
        res = self.check_done_conditions()
        self.action_done()
        if self._should_skip_scan_source_location():
            self._set_messagge_info(
                "success", _("Operation recorded. Scan next Product or lot")
            )
        else:
            self._set_messagge_info(
                "success", _("Operation recorded. Scan next source location")
            )
        return res

    def process_barcode(self, barcode):
        location, product, lot, extra = self._pre_process_barcode(barcode)
        if self._should_skip_scan_source_location():
            self.location_src_scanned = True
        # 1st - scan src location.
        if not self.location_src_scanned:
            return self._process_barcode_01_source_loc(location)
        # 2nd - scan product /lot.
        elif self.location_src_scanned and not self.product_and_lot_scanned:
            res = self._process_barcode_02_lot_and_product(product, lot)
            # Do not return when `res` is None.
            if isinstance(res, bool):
                return res
        # 3rd - scan dest location.
        elif (
            self.location_src_scanned
            and self.product_and_lot_scanned
            and not self.location_dest_scanned
        ):
            return self._process_barcode_03_dest_loc(location, product, lot, extra)
        return super().process_barcode(barcode)

    def _clean_operation_progress(self):
        if not self._should_skip_scan_source_location():
            self.location_src_scanned = False
        self.product_and_lot_scanned = False
        self.location_dest_scanned = False
        self.with_context(__barcodes_reset_qty=True).reset_qty()

    def action_done(self):
        res = super().action_done()
        if self.check_done_conditions():
            self._clean_operation_progress()
        return res

    def reset_qty(self):
        if (
            self.env.context.get("__barcodes_reset_qty", False)
            or not self.next_move_line_id
        ):
            if (
                self.next_move_line_id.stock_barcodes_sequence
                == SEQUENCE_FORCE_OPERATION
            ):
                self.next_move_line_id.write(
                    {"stock_barcodes_sequence": SEQUENCE_DO_NOT_DISPLAY}
                )
            return super().reset_qty()

    def button_picked_qty_all(self):
        self.product_qty = self.next_product_uom_qty - self.next_product_done_qty
        # Skip scan of dest location in some situations:
        if self._can_complete_without_scanning_dest_location():
            return self._mark_location_dest_done()
        res = self.action_done()
        return res

    def button_picked_qty_plus(self):
        self.product_qty += 1
        return True

    def button_picked_qty_minus(self):
        self.product_qty = max(0, self.product_qty - 1)
        return True

    def button_picked_validate(self):
        res = self.action_done()
        return res

    def button_skip_operation(self):
        self.ensure_one()
        self._clean_operation_progress()
        move_lines = (self.picking_id.move_line_ids - self.next_move_line_id).filtered(
            lambda ml: ml.qty_done < ml.product_uom_qty
        )
        if move_lines:
            last = max(move_lines.mapped("stock_barcodes_sequence"))
            self.next_move_line_id.stock_barcodes_sequence = last + 1
        else:
            # current action is the last one, mark to not be displayed
            self.next_move_line_id.stock_barcodes_sequence = SEQUENCE_DO_NOT_DISPLAY

    def button_mark_location_dest_done(self):
        return self._mark_location_dest_done()

    def _allow_change_location(self, location, location_field="src", raise_error=True):
        """
        Is the scanned location allowed to be the new source or destination location?
        :param location: the scanned location
        :param location_field: 2 options, source ('src') or destination ('dest')
        :return: a boolean. True if allowed, False if not.
        """
        if location_field == "src":
            move_location = self.next_move_line_id.move_id.location_id
            user_word = _("source")
        elif location_field == "dest":
            move_location = self.next_move_line_id.move_id.location_dest_id
            user_word = _("destination")
        else:
            raise ValidationError(
                _("Invalid value '%s' in arguments.") % location_field
            )
        # TODO: migration note. Use `is_sublocation_of` in stock_helper OCA module.
        child_locations = self.env["stock.location"].search(
            [("id", "child_of", [move_location.id])]
        )
        if location not in child_locations:
            error_msg = _(
                "The selected location '%s' cannot be set as the %s location "
                "of this operation. Only sublocations of '%s' are allowed."
            ) % (location.name, user_word, move_location.name)
            if raise_error:
                raise ValidationError(error_msg)
            self._set_messagge_info("location_no_match", error_msg)
            return False
        return True

    def action_change_location(self):
        self.ensure_one()
        location = self.env["stock.location"].search(
            [("barcode", "=", self.env.context.get("default_location_name"))]
        )
        if location and self.next_move_line_id:
            if not self.location_src_scanned:
                if self._allow_change_location(
                    location, location_field="src", raise_error=False
                ):
                    self.next_move_line_id.write(
                        {
                            "location_id": location.id,
                            "stock_barcodes_sequence": SEQUENCE_FORCE_OPERATION,
                        }
                    )
            elif not self.location_dest_scanned:
                if self._allow_change_location(
                    location, location_field="dest", raise_error=False
                ):
                    self.next_move_line_id.write(
                        {
                            "location_dest_id": location.id,
                            "stock_barcodes_sequence": SEQUENCE_FORCE_OPERATION,
                        }
                    )
                    self._set_messagge_info("info", _("Scan the destination location."))
