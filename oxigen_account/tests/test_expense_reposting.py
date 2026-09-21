# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests import Form, tagged

from odoo.addons.hr_expense.tests.common import TestExpenseCommon


@tagged("post_install", "-at_install")
class TestExpenseReposting(TestExpenseCommon):
    def _create_sheet(self, amounts=(100,), currency=None):
        currency = currency or self.env.company.currency_id
        sheet = self.env["hr.expense.sheet"].create(
            {
                "name": "Expense reposting test",
                "employee_id": self.expense_employee.id,
                "journal_id": self.company_data["default_journal_misc"].id,
                "accounting_date": "2017-01-01",
                "expense_line_ids": [
                    (
                        0,
                        0,
                        {
                            "name": "Test expense",
                            "employee_id": self.expense_employee.id,
                            "product_id": self.product_a.id,
                            "unit_amount": amount,
                            "quantity": 1,
                            "date": "2017-01-01",
                            "currency_id": currency.id,
                            "tax_ids": [(6, 0, [])],
                            "payment_mode": "own_account",
                        },
                    )
                    for amount in amounts
                ],
            }
        )
        sheet.action_submit_sheet()
        sheet.approve_expense_sheets()
        sheet.action_sheet_move_create()
        self.assertEqual(sheet.state, "post")
        return sheet

    def _pay_sheet(self, sheet, amount=100):
        action = sheet.action_register_payment()
        with Form(
            self.env["account.payment.register"].with_context(action["context"])
        ) as form:
            form.journal_id = self.company_data["default_journal_bank"]
            form.payment_date = "2017-01-01"
            form.currency_id = sheet.currency_id
            form.amount = amount
        payment_action = form.save().action_create_payments()
        return self.env["account.payment"].browse(payment_action["res_id"])

    def _accounting_values(self, move):
        return move.line_ids.read(
            [
                "account_id",
                "date",
                "debit",
                "credit",
                "currency_id",
                "amount_currency",
                "amount_residual",
                "amount_residual_currency",
                "matched_debit_ids",
                "matched_credit_ids",
                "full_reconcile_id",
            ],
            load=False,
        )

    def _preserving_reset(self, move):
        # The existing form button supplies this context to button_draft.
        move.with_context(dont_unreconcile_items=True).button_draft()
        self.assertEqual(move.state, "draft")

    def test_paid_sheet_recovers_paid_after_partner_correction(self):
        sheet = self._create_sheet()
        payment = self._pay_sheet(sheet)
        self.assertEqual(sheet.state, "done")
        before = self._accounting_values(sheet.account_move_id)
        payment_before = self._accounting_values(payment.move_id)
        self._preserving_reset(sheet.account_move_id)
        self.assertEqual(sheet.state, "post")
        sheet.account_move_id.partner_id = self.partner_b
        sheet.account_move_id.line_ids.write({"partner_id": self.partner_b.id})
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "done")
        self.assertEqual(sheet.expense_line_ids.state, "done")
        self.assertEqual(self._accounting_values(sheet.account_move_id), before)
        self.assertEqual(self._accounting_values(payment.move_id), payment_before)
        self.assertEqual(payment.state, "posted")

    def test_paid_sheet_with_zero_expense_recovers_paid(self):
        sheet = self._create_sheet((100, 0))
        self._pay_sheet(sheet)
        before = self._accounting_values(sheet.account_move_id)
        self._preserving_reset(sheet.account_move_id)
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "done")
        self.assertEqual(sheet.expense_line_ids.mapped("state"), ["done", "done"])
        self.assertEqual(self._accounting_values(sheet.account_move_id), before)

    def test_partial_payment_stays_posted(self):
        sheet = self._create_sheet()
        self._pay_sheet(sheet, 40)
        before = self._accounting_values(sheet.account_move_id)
        self._preserving_reset(sheet.account_move_id)
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "post")
        self.assertEqual(sheet.amount_residual, 60)
        self.assertEqual(self._accounting_values(sheet.account_move_id), before)

    def test_unpaid_sheet_stays_posted(self):
        sheet = self._create_sheet()
        self._preserving_reset(sheet.account_move_id)
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "post")
        self.assertEqual(sheet.amount_residual, 100)

    def test_standard_reset_still_removes_reconciliation(self):
        sheet = self._create_sheet()
        self._pay_sheet(sheet)
        sheet.account_move_id.button_draft()
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "post")
        self.assertEqual(sheet.amount_residual, 100)

    def test_batch_reposting_only_marks_settled_sheet_paid(self):
        paid_sheet = self._create_sheet()
        self._pay_sheet(paid_sheet)
        unpaid_sheet = self._create_sheet()
        moves = paid_sheet.account_move_id + unpaid_sheet.account_move_id
        moves.with_context(dont_unreconcile_items=True).button_draft()
        moves.action_post()
        self.assertEqual(paid_sheet.state, "done")
        self.assertEqual(unpaid_sheet.state, "post")
        self.assertEqual(unpaid_sheet.amount_residual, 100)

    def test_reposting_existing_payment_recovers_paid_sheet(self):
        sheet = self._create_sheet()
        payment = self._pay_sheet(sheet)
        before = self._accounting_values(payment.move_id)
        payment.with_context(dont_unreconcile_items=True).action_draft()
        self.assertEqual(sheet.state, "post")
        payment.action_post()
        self.assertEqual(sheet.state, "done")
        self.assertEqual(self._accounting_values(payment.move_id), before)

    def test_reposting_payment_does_not_pay_draft_expense_entry(self):
        sheet = self._create_sheet()
        payment = self._pay_sheet(sheet)
        self._preserving_reset(sheet.account_move_id)
        payment.with_context(dont_unreconcile_items=True).action_draft()
        payment.action_post()
        self.assertEqual(sheet.account_move_id.state, "draft")
        self.assertEqual(sheet.state, "post")

    def test_reposting_expense_waits_for_draft_payment(self):
        sheet = self._create_sheet()
        payment = self._pay_sheet(sheet)
        self._preserving_reset(sheet.account_move_id)
        payment.with_context(dont_unreconcile_items=True).action_draft()
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "post")
        payment.action_post()
        self.assertEqual(sheet.state, "done")

    def test_reposting_counterpart_without_direct_expense_link(self):
        sheet = self._create_sheet()
        payment = self.env["account.payment"].create(
            {
                "payment_type": "outbound",
                "partner_type": "supplier",
                "partner_id": self.expense_employee.address_home_id.id,
                "journal_id": self.company_data["default_journal_bank"].id,
                "amount": 100,
                "date": "2017-01-01",
                "payment_method_id": self.env.ref(
                    "account.account_payment_method_manual_out"
                ).id,
            }
        )
        payment.action_post()
        lines = sheet.account_move_id.line_ids + payment.move_id.line_ids
        lines.filtered(lambda line: line.account_internal_type == "payable").reconcile()
        self.assertEqual(sheet.state, "done")
        self.assertFalse(payment.move_id.line_ids.expense_id)
        self._preserving_reset(sheet.account_move_id)
        payment.with_context(dont_unreconcile_items=True).action_draft()
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "post")
        payment.action_post()
        self.assertEqual(sheet.state, "done")

    def test_foreign_currency_settlement_is_preserved(self):
        sheet = self._create_sheet(currency=self.currency_data["currency"])
        self._pay_sheet(sheet)
        self.assertEqual(sheet.state, "done")
        before = self._accounting_values(sheet.account_move_id)
        self._preserving_reset(sheet.account_move_id)
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "done")
        self.assertEqual(self._accounting_values(sheet.account_move_id), before)

    def test_offsetting_open_items_are_not_paid(self):
        sheet = self._create_sheet((100, -100))
        self.assertEqual(sheet.amount_residual, 0)
        self._preserving_reset(sheet.account_move_id)
        sheet.account_move_id.action_post()
        self.assertEqual(sheet.state, "post")
        self.assertFalse(any(sheet.account_move_id.line_ids.mapped("reconciled")))
