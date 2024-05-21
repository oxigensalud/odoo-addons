# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class OxigenAccountJournalLedgerWizard(models.TransientModel):
    _name = "oxigen.account.journal.ledger.wizard"
    _description = "Oxigen Account Journal Ledger Wizard"

    company_ids = fields.Many2many(
        comodel_name="res.company",
        relation="oxigen_journal_ledger_wizard_company_rel",
        column1="oxigen_journal_ledger_wizard_id",
        column2="company_id",
        required=True,
        domain=lambda self: [("id", "in", self.env.user.company_ids.ids)],
    )
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)

    @api.constrains("date_from", "date_to")
    def _check_same_year(self):
        for rec in self:
            if rec.date_from.year != rec.date_to.year:
                raise UserError(_("The dates must be in the same year"))

    @api.constrains("company_ids")
    def _check_allowed_companies(self):
        for rec in self:
            invalid_companies = rec.company_ids - self.env.user.company_ids
            if invalid_companies:
                raise UserError(
                    _(
                        "You don't have permission to access the following companies: %s"
                        % invalid_companies.mapped("name")
                    )
                )

    def _print_report(self, report_type):
        self.ensure_one()
        report_name = "report_oxigen_account_journal_ledger_csv"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(
                self,
                data={
                    "company_ids": self.company_ids.ids,
                    "date_from": self.date_from,
                    "date_to": self.date_to,
                },
            )
        )

    def button_export_csv(self):
        self.ensure_one()
        report_type = "csv"
        return self._print_report(report_type)
