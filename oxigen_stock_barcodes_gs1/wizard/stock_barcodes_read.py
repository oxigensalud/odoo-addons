# Copyright 2021-22 ForgeFlow S.L.
# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
from datetime import datetime

from odoo import _, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def process_lot(self, barcode_decoded):
        res = super().process_lot(barcode_decoded)
        if self.product_id.tracking == "serial":
            lot_barcode = barcode_decoded.get("21", False)
            operation = getattr(self, "picking_id", False) or getattr(
                self, "inventory_id", False
            )
            if not operation:
                raise ValidationError(
                    _(
                        "This record has inconsistent data. Delete the record and recreate it."
                    )
                )
            lot = self.env["stock.production.lot"].search(
                [
                    ("name", "=", lot_barcode),
                    ("product_id", "=", self.product_id.id),
                    ("company_id", "=", operation.company_id.id),
                ]
            )
            ref_barcode = barcode_decoded.get("10", False)
            if lot and ref_barcode and lot.ref != ref_barcode:
                self._set_messagge_info(
                    "not_found",
                    _(
                        "The lot %s has been found but the reference %s does not match."
                        % (lot_barcode, ref_barcode)
                    ),
                )
                return False
            if not lot and self.option_group_id.create_lot:
                lot = self._create_lot(barcode_decoded)
            self.lot_id = lot
        if self.lot_id and (self.manual_entry or self.is_manual_qty):
            self.product_qty += 1
        return res

    # WARNING: override standard method
    def process_barcode(self, barcode):  # noqa: C901
        """Only has been implemented AI (01, 02, 10, 21, 37), so is possible that
        scanner reads a barcode ok but this one is not precessed.
        """
        try:
            barcode_decoded = self.env["gs1_barcode"].decode(barcode)
        except Exception:
            return super().process_barcode(barcode)
        processed = False
        # START OF CHANGES
        package_barcode = barcode_decoded.get("02", False)
        product_barcode = barcode_decoded.get("01", False)
        # END OF CHANGES
        if not product_barcode:
            # Sometimes the product does not yet have a GTIN. In this case
            # try the AI 240 'Additional product identification assigned
            # by the manufacturer'.
            product_barcode = barcode_decoded.get("240", False)
        product_qty = barcode_decoded.get("37", False)
        if product_barcode:
            # Flushing the relevant fields of the involved models
            self.env["product.product"].flush(["barcode"])
            self.env["product.template"].flush(["company_id"])
            self.env.cr.execute(
                """
                SELECT pp.id
                FROM product_product pp
                JOIN product_template pt ON pp.product_tmpl_id = pt.id
                WHERE LOWER(LPAD(pp.barcode, 14, '0')) = LOWER(%s)
                AND (pt.company_id = %s OR pt.company_id IS NULL);
                """,
                (product_barcode, self.env.company.id),
            )
            products = self.env.cr.fetchall()
            product = self.env["product.product"].browse([x[0] for x in products])
            if len(product) > 1:
                self._set_messagge_info(
                    "not_found",
                    _("The next products have the same barcode: %s")
                    % product.mapped("barcode"),
                )
                return False
            if not product and not package_barcode:
                # If we did not found a product and we have not a package, maybe we
                # can try to use this product barcode as a packaging barcode
                package_barcode = product_barcode
            elif not product:
                self._set_messagge_info("not_found", _("Barcode for product not found"))
                return False
            else:
                processed = True
                self.action_product_scaned_post(product)
        if package_barcode:
            value_returned = self.process_barcode_package(package_barcode, processed)
            if value_returned is not None:
                return value_returned
        if self.product_id.tracking == "serial":
            lot_barcode = barcode_decoded.get("21", False)
        else:
            lot_barcode = barcode_decoded.get("10", False)
        if lot_barcode and self.product_id.tracking != "none":
            if not self.process_lot(barcode_decoded):
                return False
            processed = True
        if product_qty and package_barcode:
            # If we have processed a package, we need to multiply it
            product_qty = self._process_product_qty_gs1(product_qty)
            self.product_qty = self.product_qty * product_qty
        elif product_qty:
            product_qty = self._process_product_qty_gs1(product_qty)
            self.product_qty = product_qty
        if not self.product_qty:
            # This could happen with double GS1-128 barcodes
            if self.packaging_id:
                self.packaging_qty = 0.0 if self.manual_entry else 1.0
                self.product_qty = self.packaging_id.qty * self.packaging_qty
            else:
                self.product_qty = 0.0 if self.manual_entry else 1.0
        if processed:
            if not self.check_option_required():
                return False
            self.action_done()
            self._set_messagge_info("success", _("Barcode read correctly"))
            return True
        return super().process_barcode(barcode)

    def _prepare_lot_values(self, barcode_decoded):
        res = super()._prepare_lot_values(barcode_decoded)
        if not res.get("product_id"):
            product_barcode = barcode_decoded.get("01", False)
            product = self.env["product.product"].search(
                self._barcode_domain(product_barcode)
            )
            if product:
                res["product_id"] = product.id
        removal_date_str = barcode_decoded.get("17", False)
        if removal_date_str:
            try:
                removal_datetime = datetime.strptime(removal_date_str, "%Y-%m-%d")
                res["removal_date"] = removal_datetime
            except ValueError:
                _logger.error("Cannot convert GS1 removal date.")
        return res
