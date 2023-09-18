# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestEquipmentFromPurchase(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Demo Partner"})
        cls.product = cls.env["product.template"].create(
            {
                "name": "My Product",
                "type": "product",
                "tracking": "serial",
                "maintenance_lot": True,
            }
        )
        cls.purchase = cls.env["purchase.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.product.product_variant_id.id,
                            "name": cls.product.name,
                        },
                    )
                ],
            }
        )

    def test_equipment_creation(self):
        self.purchase.button_confirm()
        picking = self.purchase.picking_ids
        self.assertTrue(picking)
        picking.move_ids_without_package.move_line_ids.write(
            {
                "lot_name": "1234",
                "qty_done": 1,
            }
        )
        self.assertFalse(picking.maintenance_equipment_ids)
        picking.button_validate()
        self.assertTrue(picking.maintenance_equipment_ids)
        action = (
            picking.move_ids_without_package.move_line_ids.lot_id.action_lot_open_equipment()
        )
        self.assertEqual(
            picking.maintenance_equipment_ids,
            self.env[action["res_model"]].browse(action["res_id"]),
        )
