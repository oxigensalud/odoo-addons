# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import common


class TestsaleOrder(common.SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.product = cls.env["product.product"].create(
            {
                "name": "Product Test",
                "uom_id": cls.env.ref("uom.product_uom_unit").id,
                "uom_po_id": cls.env.ref("uom.product_uom_unit").id,
            }
        )

        cls.partner_id = cls.env["res.partner"].create({"name": "Test Partner"})

        cls.sale_order = cls.env["sale.order"].create(
            {
                "name": "Test sale Order",
                "partner_id": cls.partner_id.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "DEMO",
                            "product_id": cls.product.id,
                            "product_uom": cls.product.uom_id.id,
                        },
                    )
                ],
            }
        )

        cls.request1 = cls.env["maintenance.request"].create({"name": "Request 1"})
        cls.request2 = cls.env["maintenance.request"].create({"name": "Request 2"})
        cls.sale_order.maintenance_request_ids += cls.request1
        cls.sale_order.maintenance_request_ids += cls.request2

        cls.equipment = cls.env["maintenance.equipment"].create({"name": "Equipment 1"})

        cls.partner = cls.env["res.partner"].create({"name": "Test Partner"})

    def test_compute_maintenance_request_count(self):
        self.assertEqual(self.sale_order.maintenance_request_count, 2)

    def test_action_view_maintenance_request(self):

        result = self.sale_order.action_view_maintenance_request()
        self.assertTrue(result)
        self.assertIn("context", result)
        self.assertIn("domain", result)
        self.assertIn("views", result)
        self.assertIn("res_id", result)
        self.assertEqual(
            result["context"], {"default_sale_order_id": self.sale_order.id}
        )
        self.assertIn(
            self.request1, self.env[result["res_model"]].search(result["domain"])
        )
        self.assertIn(
            self.request2, self.env[result["res_model"]].search(result["domain"])
        )

        self.sale_order.maintenance_request_ids = False
        action_result = self.sale_order.action_view_maintenance_request()
        self.assertFalse(
            self.env[action_result["res_model"]].search(action_result["domain"])
        )

        self.sale_order.maintenance_request_ids = self.request1
        action2_result = self.sale_order.action_view_maintenance_request()
        self.assertEqual(
            self.env[action2_result["res_model"]].browse(action2_result["res_id"]),
            self.request1,
        )
