# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools import formatLang


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("ref")
    def _onchange_ref(self):
        for move in self.filtered(lambda m: m.move_type != "entry"):
            move.payment_reference = move.ref
            move._inverse_payment_reference()

    @api.constrains("ref", "move_type", "partner_id", "journal_id", "state")
    def _check_duplicate_supplier_reference(self):
        """
        The code overrides the _check_duplicate_supplier_reference function of Odoo.
        """
        moves = self.filtered(
            lambda move: move.state == "posted"
            and move.is_purchase_document()
            and move.ref
        )
        if not moves:
            return

        self.env["account.move"].flush_model(
            [
                "ref",
                "move_type",
                "journal_id",
                "company_id",
                "partner_id",
                "commercial_partner_id",
            ]
        )
        self.env["account.journal"].flush_model(["company_id"])
        self.env["res.partner"].flush_model(["commercial_partner_id"])

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
                AND move2.state = 'posted'
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
                        lambda m: f"{m.partner_id.display_name} - {m.ref}"
                    )
                )
            )

    @api.depends("move_type", "line_ids.amount_residual")
    def _compute_payments_widget_reconciled_info(self):
        res = super()._compute_payments_widget_reconciled_info()
        for move in self.filtered(
            lambda moves: moves.state != "posted"
            and moves.is_invoice(include_receipts=True)
        ):
            payments_widget_vals = {
                "title": _("Less Payment"),
                "outstanding": False,
                "content": [],
            }

            reconciled_vals = []
            reconciled_partials = move.sudo()._get_all_reconciled_invoice_partials()
            for reconciled_partial in reconciled_partials:
                counterpart_line = reconciled_partial["aml"]
                if counterpart_line.move_id.ref:
                    reconciliation_ref = (
                        f"{counterpart_line.move_id.name} "
                        f"({counterpart_line.move_id.ref})"
                    )
                else:
                    reconciliation_ref = counterpart_line.move_id.name
                if (
                    counterpart_line.amount_currency
                    and counterpart_line.currency_id
                    != counterpart_line.company_id.currency_id
                ):
                    foreign_currency = counterpart_line.currency_id
                else:
                    foreign_currency = False

                reconciled_vals.append(
                    {
                        "name": counterpart_line.name,
                        "journal_name": counterpart_line.journal_id.name,
                        "company_name": counterpart_line.journal_id.company_id.name
                        if counterpart_line.journal_id.company_id != move.company_id
                        else False,
                        "amount": reconciled_partial["amount"],
                        "currency_id": move.company_id.currency_id.id
                        if reconciled_partial["is_exchange"]
                        else reconciled_partial["currency"].id,
                        "date": counterpart_line.date,
                        "partial_id": reconciled_partial["partial_id"],
                        "account_payment_id": counterpart_line.payment_id.id,
                        "payment_method_name": (
                            counterpart_line.payment_id.payment_method_line_id.name
                        ),
                        "move_id": counterpart_line.move_id.id,
                        "is_refund": counterpart_line.move_id.move_type
                        in ["in_refund", "out_refund"],
                        "ref": reconciliation_ref,
                        # these are necessary for the
                        # views to change depending on the values
                        "is_exchange": reconciled_partial["is_exchange"],
                        "amount_company_currency": formatLang(
                            self.env,
                            abs(counterpart_line.balance),
                            currency_obj=counterpart_line.company_id.currency_id,
                        ),
                        "amount_foreign_currency": foreign_currency
                        and formatLang(
                            self.env,
                            abs(counterpart_line.amount_currency),
                            currency_obj=foreign_currency,
                        ),
                    }
                )
            payments_widget_vals["content"] = reconciled_vals

            if payments_widget_vals["content"]:
                move.invoice_payments_widget = payments_widget_vals
            else:
                move.invoice_payments_widget = False
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    def remove_move_reconcile(self):
        if not self.env.context.get("dont_unreconcile_items", False):
            return super().remove_move_reconcile()
