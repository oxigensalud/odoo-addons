# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import json

from odoo import _, api, models
from odoo.tools import date_utils


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("ref")
    def _onchange_ref(self):
        for move in self.filtered(lambda m: m.move_type != "entry"):
            move.payment_reference = move.ref
            move._onchange_payment_reference()

    @api.depends("move_type", "line_ids.amount_residual")
    def _compute_payments_widget_reconciled_info(self):
        res = super()._compute_payments_widget_reconciled_info()
        for move in self.filtered(
            lambda l: l.state != "posted" and l.is_invoice(include_receipts=True)
        ):
            payments_widget_vals = {
                "title": _("Less Payment"),
                "outstanding": False,
                "content": [],
            }
            payments_widget_vals["content"] = move._get_reconciled_info_JSON_values()

            if payments_widget_vals["content"]:
                move.invoice_payments_widget = json.dumps(
                    payments_widget_vals, default=date_utils.json_default
                )
            else:
                move.invoice_payments_widget = json.dumps(False)
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        if not self.env.context.get("dont_unreconcile_items", False):
            return super().remove_move_reconcile()
