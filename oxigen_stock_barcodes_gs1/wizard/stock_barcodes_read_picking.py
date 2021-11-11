# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import logging
from datetime import datetime

from odoo import _, models

_logger = logging.getLogger(__name__)


class WizStockBarcodesReadPicking(models.TransientModel):
    _inherit = "wiz.stock.barcodes.read.picking"

    def _pre_process_barcode(self, barcode):
        try:
            barcode_decoded = self.env["gs1_barcode"].decode(barcode)
        except Exception:
            return super()._pre_process_barcode(barcode)
        product = False
        lot = False
        packaging = False
        package_barcode = barcode_decoded.get("02", False)
        product_barcode = barcode_decoded.get("01", False)
        if not product_barcode:
            # Sometimes the product does not yet have a GTIN. In this case
            # try the AI 240 'Additional product identification assigned
            # by the manufacturer'.
            product_barcode = barcode_decoded.get("240", False)
        lot_barcode = barcode_decoded.get("10", False)
        product_qty = barcode_decoded.get("37", False)
        if product_barcode:
            product = self.env["product.product"].search(
                self._barcode_domain(product_barcode)
            )

        if package_barcode:
            packaging = self.env["product.packaging"].search(
                self._barcode_domain(package_barcode)
            )

        if lot_barcode and product and product.tracking != "none":
            lot_barcode = barcode_decoded.get("10", False)
            lot_product = product or self.product_id
            lot = self.env["stock.production.lot"].search(
                [("name", "=", lot_barcode), ("product_id", "=", lot_product.id)]
            )
            if not lot:
                self._set_messagge_info(
                    "not_found", _("Lot/Serial Number not found. Please, create it.")
                )

        if product_qty:
            self.product_qty = product_qty

        # Location scanned by GS-1 not supported, returning regular scanning result.
        (
            location_no_gs1,
            product_no_gs1,
            lot_no_gs1,
            extra_data,
        ) = super()._pre_process_barcode(barcode)
        removal_date = barcode_decoded.get("17", False)
        extra_data.update(
            {
                "packaging": packaging,
                "product_qty": product_qty,
                "removal_date": removal_date,
            }
        )
        return location_no_gs1, product or product_no_gs1, lot or lot_no_gs1, extra_data

    def _prepare_lot_values(self, barcode_decoded):
        res = super(WizStockBarcodesReadPicking, self)._prepare_lot_values(
            barcode_decoded
        )
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
