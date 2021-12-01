# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import common


class TestOxigenPurchase(common.TransactionCase):
    def setUp(self):
        super(TestOxigenPurchase, self).setUp()

        self.product_obj = self.env["product.product"]
        self.partner_obj = self.env["res.partner"]
        self.po_obj = self.env["purchase.order"]
        self.pol_obj = self.env["purchase.order.line"]
        self.location_obj = self.env["stock.location"]
        self.orderpoint_obj = self.env["stock.warehouse.orderpoint"]
        self.group_obj = self.env["procurement.group"]

        self.warehouse = self.env.ref("stock.warehouse0")
        self.stock_location = self.warehouse.lot_stock_id
        route_buy = self.env.ref("purchase.route_warehouse0_buy")

        # Partners:
        self.vendor_1 = self.partner_obj.create({"name": "Vendor 1"})

        # Create products:
        self.test_product = self.product_obj.create(
            {
                "name": "Test Product 1",
                "type": "product",
                "list_price": 150.0,
                "route_ids": [(6, 0, route_buy.ids)],
                "seller_ids": [(0, 0, {"name": self.vendor_1.id, "price": 20.0})],
            }
        )

        # Create Orderpoints:
        self.op1 = self.orderpoint_obj.create(
            {
                "product_id": self.test_product.id,
                "location_id": self.stock_location.id,
                "product_min_qty": 10.0,
                "product_max_qty": 20.0,
            }
        )

    def test_01_po_from_orderpoint(self):
        in_progress = self.op1._quantity_in_progress().get(self.op1.id)
        self.assertEqual(in_progress, 0.0)
        self.group_obj.run_scheduler()
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.test_product.id)]
        )
        self.assertTrue(po_line)
        # The orderpoint must have required 20.0 units:
        self.assertEqual(po_line.product_qty, 20.0)
        in_progress = self.op1._quantity_in_progress().get(self.op1.id)
        self.assertEqual(in_progress, 20.0)

    def test_02_orderpoint_considers_manual_po(self):
        in_progress = self.op1._quantity_in_progress().get(self.op1.id)
        self.assertEqual(in_progress, 0.0)
        self.po_obj.create(
            {
                "partner_id": self.vendor_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product.id,
                            "product_qty": 8.0,
                            "name": self.test_product.name,
                            "product_uom": self.test_product.uom_id.id,
                            "price_unit": 3.0,
                            "date_planned": fields.Date.today(),
                        },
                    )
                ],
            }
        )
        in_progress = self.op1._quantity_in_progress().get(self.op1.id)
        self.assertEqual(in_progress, 8.0)
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.test_product.id)]
        )
        self.assertEqual(len(po_line), 1)
        self.assertEqual(po_line.product_qty, 8.0)
        self.group_obj.run_scheduler()
        # The orderpoint must have required 12.0 units more (20 - 8 in open rfq):
        po_line = self.env["purchase.order.line"].search(
            [("product_id", "=", self.test_product.id)]
        )
        self.assertEqual(len(po_line), 1)
        self.assertEqual(po_line.product_qty, 20.0)
        in_progress = self.op1._quantity_in_progress().get(self.op1.id)
        self.assertEqual(in_progress, 20.0)

    def test_03_picking_ref_in_po(self):
        # Draft purchase order created
        self.po = self.po_obj.create(
            {
                "partner_id": self.vendor_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product.id,
                            "product_qty": 8.0,
                            "name": self.test_product.name,
                            "product_uom": self.test_product.uom_id.id,
                            "price_unit": 3.0,
                            "date_planned": fields.Date.today(),
                        },
                    )
                ],
            }
        )
        # Purchase order confirm
        self.po.button_confirm()

        # Validate first shipment and add reference
        self.picking = self.po.picking_ids[0]
        self.picking.partner_ref = "ref 12"
        self.assertEqual(self.po.partner_ref, "ref 12", "PO doesn't have a reference")

        # Change referene again
        self.picking.partner_ref = "ref 11"
        self.assertEqual(self.po.partner_ref, "ref 11", "PO reference doesn't match")

    def test_04_picking_ref_in_po_backorder(self):
        # Draft purchase order created
        self.po = self.po_obj.create(
            {
                "partner_id": self.vendor_1.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.test_product.id,
                            "product_qty": 8.0,
                            "name": self.test_product.name,
                            "product_uom": self.test_product.uom_id.id,
                            "price_unit": 3.0,
                            "date_planned": fields.Date.today(),
                        },
                    )
                ],
            }
        )
        # Purchase order confirm
        self.po.button_confirm()

        # Validate first shipment and add reference
        self.picking = self.po.picking_ids[0]
        self.picking.partner_ref = "ref 12"
        self.picking.move_lines.quantity_done = 2

        # create the backorder
        backorder_wizard_dict = self.picking.button_validate()
        backorder_wizard = self.env[backorder_wizard_dict["res_model"]].browse(
            backorder_wizard_dict["res_id"]
        )
        backorder_wizard.process()

        self.assertTrue(
            self.env["stock.picking"].search([("backorder_id", "=", self.picking.id)]),
            "no back order created",
        )
        self.picking2 = self.env["stock.picking"].search(
            [("backorder_id", "=", self.picking.id)]
        )

        # Change backorder reference
        self.picking2.partner_ref = "ref 13"

        self.assertEqual(
            self.po.partner_ref, "ref 12, ref 13", "PO reference doesn't match"
        )
