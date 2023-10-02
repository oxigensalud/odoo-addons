# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
import json

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("ref")
    def _onchange_ref(self):
        for move in self.filtered(lambda m: m.move_type != "entry"):
            move.payment_reference = move.ref
            move._onchange_payment_reference()

    @api.constrains("ref", "move_type", "partner_id", "journal_id", "state")
    def _check_move_supplier_ref(self):
        """
        Check if an other vendor bill has the same ref
        and the same commercial_partner_id than the current instance.
        The check only makes sense when validating it
        The code has been takend from `_check_duplicate_supplier_reference` function of odoo
        """
        moves = self.filtered(
            lambda move: move.state == "posted"
            and move.is_purchase_document()
            and move.ref
        )
        if not moves:
            return

        self.env["account.move"].flush(
            [
                "ref",
                "move_type",
                "journal_id",
                "company_id",
                "partner_id",
                "commercial_partner_id",
            ]
        )
        self.env["account.journal"].flush(["company_id"])
        self.env["res.partner"].flush(["commercial_partner_id"])

        # /!\ Computed stored fields are not yet inside the database.
        self._cr.execute(
            """
            SELECT move2.id
            FROM account_move move
            JOIN account_journal journal ON journal.id = move.journal_id
            JOIN res_partner partner ON partner.id = move.partner_id
            INNER JOIN account_move move2 ON
                move2.ref = move.ref
                AND move2.company_id = journal.company_id
                AND move2.commercial_partner_id = partner.commercial_partner_id
                AND move2.move_type = move.move_type
                AND move2.id != move.id
            WHERE move.id IN %s
        """,
            [tuple(moves.ids)],
        )
        duplicated_moves = self.browse([r[0] for r in self._cr.fetchall()])
        if duplicated_moves:
            raise ValidationError(
                _(
                    "Duplicated vendor reference detected. "
                    "You probably encoded twice the same vendor bill/credit note:\n%s"
                )
                % "\n".join(
                    duplicated_moves.mapped(
                        lambda m: "%(partner)s - %(ref)s"
                        % {
                            "ref": m.ref,
                            "partner": m.partner_id.display_name,
                        }
                    )
                )
            )

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
