# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import common


class TestProductRepairCount(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.device = cls.env["product.product"].create(
            {"name": "Test repaired device", "type": "consu"}
        )
        cls.part = cls.env["product.product"].create(
            {"name": "Test repair part", "type": "consu"}
        )

    def _repair_with_part(self):
        return self.env["repair.order"].create(
            {
                "product_id": self.device.id,
                "move_ids": [
                    (
                        0,
                        0,
                        {
                            "repair_line_type": "add",
                            "product_id": self.part.id,
                            "product_uom_qty": 1.0,
                        },
                    )
                ],
            }
        )

    def _assert_repairs(self, repairs, count):
        # the stat button of the variant and of the template read these fields
        for product in (self.part, self.part.product_tmpl_id):
            self.assertEqual(product.in_repair_ids, repairs)
            self.assertEqual(product.repair_count, count)

    def test_01_no_repair(self):
        self._assert_repairs(self.env["repair.order"], 0)

    def test_02_repair_created_after_the_product(self):
        repair = self._repair_with_part()
        # draft: listed but not counted
        self._assert_repairs(repair, 0)
        repair.action_validate()
        self.assertEqual(repair.state, "confirmed")
        self._assert_repairs(repair, 1)

    def test_03_second_repair_and_cancel(self):
        first = self._repair_with_part()
        first.action_validate()
        second = self._repair_with_part()
        second.action_validate()
        self._assert_repairs(first | second, 2)
        first.action_repair_cancel()
        self.assertEqual(first.state, "cancel")
        self._assert_repairs(first | second, 1)
