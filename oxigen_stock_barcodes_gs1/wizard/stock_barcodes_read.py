# Copyright 2021-22 ForgeFlow S.L.
# Copyright NuoBiT Solutions SL - Frank Cespedes <fcespedes@nuobit.com>
# Copyright NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, models
from odoo.exceptions import ValidationError


class WizStockBarcodesRead(models.AbstractModel):
    _inherit = "wiz.stock.barcodes.read"

    def _prepare_serial_lot_values(self, barcode_decoded):
        lot_barcode = barcode_decoded.get("21", False)
        ref_barcode = barcode_decoded.get("10", False)
        return {
            "name": lot_barcode,
            "ref": ref_barcode,
            "product_id": self.product_id.id,
            "company_id": self.env.company.id,
        }

    def _create_serial_lot(self, barcode_decoded):
        return self.env["stock.lot"].create(
            self._prepare_serial_lot_values(barcode_decoded)
        )

    def process_serial_lot(self, barcode_decoded):
        operation = getattr(self, "picking_id", False) or getattr(
            self, "inventory_id", False
        )
        if not operation:
            raise ValidationError(
                _(
                    "This record has inconsistent data. "
                    "Delete the record and recreate it."
                )
            )
        lot_barcode = barcode_decoded.get("21", False)
        if lot_barcode:
            lot = self.env["stock.lot"].search(
                [
                    ("name", "=", lot_barcode),
                    ("product_id", "=", self.product_id.id),
                    ("company_id", "=", operation.company_id.id),
                ]
            )
            if lot:
                ref_barcode = barcode_decoded.get("10", False)
                if ref_barcode and lot.ref != ref_barcode:
                    self._set_messagge_info(
                        "not_found",
                        _(
                            "The lot %(lot)s has been found but"
                            " the reference %(ref)s does not match."
                        )
                        % {"lot": lot_barcode, "ref": ref_barcode},
                    )
                    return False
            else:
                if self.option_group_id.create_lot:
                    lot = self._create_serial_lot(barcode_decoded)
            if lot:
                self.lot_id = lot
        return True

    def _process_ai_10(self, gs1_list):
        res = super()._process_ai_10(gs1_list)
        if res and self.lot_id and (self.manual_entry or self.is_manual_qty):
            self.product_qty += 1
        return res

    def _process_ai_02(self, gs1_list):
        if self._is_lot_ai_in_barcode(gs1_list):
            self = self.with_context(skip_set_info_from_quants=True)

        products = self.env["product.product"].search(
            [
                ("barcode", "=ilike", "%" + self.barcode.lstrip("0")),
                ("company_id", "in", (self.env.company.id, False)),
            ]
        )
        product = products.barcode_ids.filtered(
            lambda x: x.name.zfill(14) == self.barcode
        ).product_id

        if len(product) > 1:
            self._set_messagge_info(
                "not_found",
                _("The next products have the same barcode: %s")
                % product.mapped("barcode"),
            )
            return False

        if not product:
            packaging_ai = next(filter(lambda f: f["ai"] == "01", gs1_list), False)
            if not packaging_ai:
                return self._process_ai_01(gs1_list)
            return False

        self.action_product_scaned_post(product)
        return True

    def _process_ai_21(self, gs1_list):
        if self.product_id and self.product_id.tracking == "serial":
            barcode_decoded = {item["ai"]: item["value"] for item in gs1_list}
            if not self.process_serial_lot(barcode_decoded):
                return False
            return True
        lot_ai = next(filter(lambda f: f["ai"].startswith("10"), gs1_list), False)
        if lot_ai:
            return True
        return super()._process_ai_21(gs1_list=gs1_list)
