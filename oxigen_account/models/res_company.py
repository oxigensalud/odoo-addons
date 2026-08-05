from odoo import _, models
from odoo.exceptions import RedirectWarning


class ResCompany(models.Model):
    _inherit = "res.company"

    def _validate_fiscalyear_lock(self, values):
        # WARNING: Overriding standard method

        if values.get("fiscalyear_lock_date"):
            # START OF CHANGES
            draft_entries = self.env["account.move"].search(
                [
                    ("company_id", "=", self.ids),
                    ("state", "=", "draft"),
                    ("date", "<=", values["fiscalyear_lock_date"]),
                ]
            )
            if draft_entries:
                # return self._action_move_from_draft()
                error_msg = _(
                    "There are still unposted entries in the period you want to lock."
                )
                action_error = self._action_move_from_draft(
                    values["fiscalyear_lock_date"],
                    values["tax_lock_date"],
                    values["period_lock_date"],
                )
                # draft_entries_res = {}
                raise RedirectWarning(
                    error_msg, action_error, _("Change/Show draft entries")
                )
            # END OF CHANGES
            unreconciled_statement_lines = self.env[
                "account.bank.statement.line"
            ].search(
                [
                    ("company_id", "in", self.ids),
                    ("is_reconciled", "=", False),
                    ("date", "<=", values["fiscalyear_lock_date"]),
                    ("move_id.state", "in", ("draft", "posted")),
                ]
            )
            if unreconciled_statement_lines:
                error_msg = _(
                    "There are still unreconciled bank statement lines in the period "
                    "you want to lock. You should either reconcile or delete them."
                )
                action_error = {
                    "type": "ir.actions.client",
                    "tag": "bank_statement_reconciliation_view",
                    "context": {
                        "statement_line_ids": unreconciled_statement_lines.ids,
                        "company_ids": self.env.company.ids,
                    },
                }
                raise RedirectWarning(
                    error_msg, action_error, _("Show Unreconciled Bank Statement Line")
                )

    def _action_move_from_draft(
        self, fiscalyear_lock_date, tax_lock_date, period_lock_date
    ):
        ctx = self.env.context.copy()
        ctx["fiscalyear_lock_date"] = fiscalyear_lock_date
        ctx["tax_lock_date"] = tax_lock_date
        ctx["period_lock_date"] = period_lock_date
        view = self.env.ref("oxigen_account.view_change_draft_date")
        return {
            "name": _("Change draft entries date?"),
            "type": "ir.actions.act_window",
            "res_model": "account.update.lock_date",
            "view_mode": "form",
            "views": [(view.id, "form")],
            "target": "new",
            "view_id": view.id,
            "context": ctx,
        }
