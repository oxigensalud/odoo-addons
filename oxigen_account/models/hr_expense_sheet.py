# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    def _set_paid_if_fully_reconciled(self):
        """Restore the workflow after reposting settled accounting entries."""
        sheets = self.filtered(
            lambda sheet: sheet.payment_mode == "own_account"
            and sheet.state == "post"
            and sheet.account_move_id.state == "posted"
        )
        for sheet in sheets:
            payable_lines = sheet.account_move_id.line_ids.filtered(
                lambda line: line.account_internal_type in ("payable", "receivable")
            )
            counterpart_lines = (
                payable_lines.matched_debit_ids.debit_move_id
                | payable_lines.matched_credit_ids.credit_move_id
            )
            if (
                payable_lines
                and all(payable_lines.mapped("reconciled"))
                and all(move.state == "posted" for move in counterpart_lines.move_id)
            ):
                sheet.set_to_paid()
