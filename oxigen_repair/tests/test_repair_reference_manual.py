# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestRepairReferenceManual(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company = cls.env.company
        cls.other_company = cls.env["res.company"].create(
            {"name": "Test company with sequence reference"}
        )
        cls.product = cls.env["product.product"].create(
            {"name": "Test repair product", "type": "consu", "is_storable": True}
        )
        cls.Repair = cls.env["repair.order"]
        cls.placeholder = cls.Repair._repair_reference_placeholder()

    def _repair_vals(self, company, **extra):
        vals = {"product_id": self.product.id, "company_id": company.id}
        vals.update(extra)
        return vals

    def _picking_type(self, company):
        # default repair operation type of the company: core numbers the
        # order from its sequence
        picking_type_id = self.Repair.with_company(company).default_get(
            ["picking_type_id"]
        )["picking_type_id"]
        return self.env["stock.picking.type"].browse(picking_type_id)

    def _next_number(self, company=None):
        sequence = self._picking_type(company or self.company).sequence_id
        # computed field, cached: drop the cache to read the real next value
        sequence.invalidate_recordset(["number_next_actual"])
        return sequence.number_next_actual

    def _assert_numbered(self, name):
        self.assertTrue(name)
        self.assertNotEqual(name, self.placeholder)

    def test_01_flag_off_default_and_create_numbered(self):
        self.company.repair_reference_manual = False
        before = self._next_number()
        self.assertEqual(self.Repair.default_get(["name"])["name"], self.placeholder)
        self.assertEqual(self._next_number(), before)
        repair = self.Repair.create(self._repair_vals(self.company))
        self._assert_numbered(repair.name)
        self.assertEqual(self._next_number(), before + 1)

    def test_02_flag_on_default_blank_sequence_untouched(self):
        self.company.repair_reference_manual = True
        before = self._next_number()
        self.assertFalse(self.Repair.default_get(["name"]).get("name"))
        self.assertEqual(self._next_number(), before)

    def test_03_flag_on_manual_name_kept(self):
        self.company.repair_reference_manual = True
        before = self._next_number()
        repair = self.Repair.create(
            self._repair_vals(self.company, name="AMB-2026-001")
        )
        self.assertEqual(repair.name, "AMB-2026-001")
        self.assertEqual(self._next_number(), before)

    def test_04_flag_on_empty_or_placeholder_refused_on_create(self):
        self.company.repair_reference_manual = True
        before = self._next_number()
        for vals in (
            self._repair_vals(self.company),
            self._repair_vals(self.company, name=""),
            self._repair_vals(self.company, name=self.placeholder),
        ):
            with self.assertRaises(ValidationError):
                self.Repair.create(vals)
        self.assertEqual(self._next_number(), before)

    def test_06_other_company_without_flag_unaffected(self):
        self.company.repair_reference_manual = True
        self.other_company.repair_reference_manual = False
        Repair = self.Repair.with_company(self.other_company)
        before = self._next_number(self.other_company)
        self.assertEqual(Repair.default_get(["name"])["name"], self.placeholder)
        repair = Repair.create(self._repair_vals(self.other_company))
        self._assert_numbered(repair.name)
        self.assertEqual(self._next_number(self.other_company), before + 1)

    def test_07_settings_write_the_company_flag(self):
        settings = self.env["res.config.settings"].create(
            {"repair_reference_manual": True}
        )
        settings.execute()
        self.assertTrue(self.company.repair_reference_manual)
        settings = self.env["res.config.settings"].create(
            {"repair_reference_manual": False}
        )
        settings.execute()
        self.assertFalse(self.company.repair_reference_manual)

    def test_08_flagged_company_from_context_default(self):
        # user in a company without the flag, order created for a flagged
        # one through the default of company_id (the operation type must be
        # the one of that company, as the form fills it)
        self.company.repair_reference_manual = False
        self.other_company.repair_reference_manual = True
        before = self._next_number(self.other_company)
        Repair = self.Repair.with_context(default_company_id=self.other_company.id)
        self.assertFalse(Repair.default_get(["name"]).get("name"))
        self.assertEqual(self._next_number(self.other_company), before)
        vals = self._repair_vals(
            self.other_company,
            picking_type_id=self._picking_type(self.other_company).id,
        )
        del vals["company_id"]
        with self.assertRaises(ValidationError):
            Repair.create(vals)
        self.assertEqual(self._next_number(self.other_company), before)

    def test_09_unflagged_company_from_context_default(self):
        # user in a flagged company, order created for a company with the
        # sequence through the default of company_id
        self.company.repair_reference_manual = True
        self.other_company.repair_reference_manual = False
        Repair = self.Repair.with_context(default_company_id=self.other_company.id)
        self.assertEqual(Repair.default_get(["name"])["name"], self.placeholder)
        vals = self._repair_vals(
            self.other_company,
            picking_type_id=self._picking_type(self.other_company).id,
        )
        del vals["company_id"]
        repair = Repair.create(vals)
        self.assertEqual(repair.company_id, self.other_company)
        self._assert_numbered(repair.name)

    def _other_picking_type(self, company):
        return self.env["stock.picking.type"].create(
            {
                "name": "Test repair operation type",
                "code": "repair_operation",
                "sequence_code": "TRO",
                "company_id": company.id,
                "warehouse_id": self._picking_type(company).warehouse_id.id,
            }
        )

    def test_10_flag_on_operation_type_change_keeps_name(self):
        self.company.repair_reference_manual = True
        repair = self.Repair.create(
            self._repair_vals(self.company, name="AMB-2026-001")
        )
        repair.write({"picking_type_id": self._other_picking_type(self.company).id})
        self.assertEqual(repair.name, "AMB-2026-001")

    def test_11_flag_off_operation_type_change_numbered_again(self):
        self.company.repair_reference_manual = False
        repair = self.Repair.create(self._repair_vals(self.company))
        name = repair.name
        repair.write({"picking_type_id": self._other_picking_type(self.company).id})
        self._assert_numbered(repair.name)
        self.assertNotEqual(repair.name, name)
