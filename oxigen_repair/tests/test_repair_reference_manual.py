# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import common


class TestRepairReferenceManual(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.company = self.env.company
        self.other_company = self.env["res.company"].create(
            {"name": "Test company with sequence reference"}
        )
        sequences = self.env["ir.sequence"].search([("code", "=", "repair.order")])
        self.assertEqual(len(sequences), 1)
        self.sequence = sequences
        self.product = self.env["product.product"].create(
            {"name": "Test repair product", "type": "product"}
        )
        # shared location (no company): valid for any company's repair order
        self.location = self.env["stock.location"].create(
            {"name": "Test repair location", "usage": "internal", "company_id": False}
        )
        self.Repair = self.env["repair.order"]

    def _repair_vals(self, company, **extra):
        vals = {
            "product_id": self.product.id,
            "product_uom": self.product.uom_id.id,
            "location_id": self.location.id,
            "company_id": company.id,
        }
        vals.update(extra)
        return vals

    def _next_number(self):
        # computed field, cached: drop the cache to read the real next value
        self.sequence.invalidate_cache(fnames=["number_next_actual"])
        return self.sequence.number_next_actual

    def _assert_numbered(self, name):
        self.assertTrue(name)
        self.assertFalse(name.startswith("/"))

    def test_01_flag_off_default_and_create_numbered(self):
        self.company.repair_reference_manual = False
        before = self._next_number()
        self._assert_numbered(self.Repair.default_get(["name"])["name"])
        self.assertEqual(self._next_number(), before + 1)
        repair = self.Repair.create(self._repair_vals(self.company))
        self._assert_numbered(repair.name)
        self.assertEqual(self._next_number(), before + 2)

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

    def test_04_flag_on_empty_or_slash_refused_on_create(self):
        self.company.repair_reference_manual = True
        before = self._next_number()
        for vals in (
            self._repair_vals(self.company),
            self._repair_vals(self.company, name=""),
            self._repair_vals(self.company, name="/"),
        ):
            with self.assertRaises(ValidationError):
                self.Repair.create(vals)
        self.assertEqual(self._next_number(), before)

    def test_06_other_company_without_flag_unaffected(self):
        self.company.repair_reference_manual = True
        self.other_company.repair_reference_manual = False
        Repair = self.Repair.with_company(self.other_company)
        self._assert_numbered(Repair.default_get(["name"])["name"])
        repair = Repair.create(self._repair_vals(self.other_company))
        self._assert_numbered(repair.name)

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
        # user in a company without the flag, form opened for a flagged one
        self.company.repair_reference_manual = False
        self.other_company.repair_reference_manual = True
        before = self._next_number()
        Repair = self.Repair.with_context(default_company_id=self.other_company.id)
        self.assertFalse(Repair.default_get(["name"]).get("name"))
        self.assertEqual(self._next_number(), before)
        vals = self._repair_vals(self.other_company)
        del vals["company_id"]
        with self.assertRaises(ValidationError):
            Repair.create(vals)
        self.assertEqual(self._next_number(), before)

    def test_09_unflagged_company_from_context_default(self):
        # user in a flagged company, form opened for a company with the sequence
        self.company.repair_reference_manual = True
        self.other_company.repair_reference_manual = False
        Repair = self.Repair.with_context(default_company_id=self.other_company.id)
        self._assert_numbered(Repair.default_get(["name"])["name"])
        vals = self._repair_vals(self.other_company)
        del vals["company_id"]
        repair = Repair.create(vals)
        self.assertEqual(repair.company_id, self.other_company)
        self._assert_numbered(repair.name)
