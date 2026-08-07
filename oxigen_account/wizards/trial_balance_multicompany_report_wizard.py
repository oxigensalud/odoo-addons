# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import date_utils


class TrialBalanceMulticompanyReportWizard(models.TransientModel):
    """Trial balance report wizard for consolidated companies"""

    _name = "trial.balance.multicompany.report.wizard"
    _description = "Consolidated Trial Balance Report Wizard"
    _inherit = "account_financial_report_abstract_wizard"

    company_ids = fields.Many2many(
        "res.company",
        default=lambda self: self.env.companies,
        required=True,
        string="Companies",
    )
    date_range_id = fields.Many2one(comodel_name="date.range", string="Date range")
    date_from = fields.Date(required=True)
    date_to = fields.Date(required=True)
    target_move = fields.Selection(
        [("posted", "All Posted Entries"), ("all", "All Entries")],
        string="Target Moves",
        required=True,
        default="posted",
    )
    show_hierarchy = fields.Boolean(
        string="Show hierarchy",
        help="Use when your account groups are hierarchical",
    )
    limit_hierarchy_level = fields.Boolean("Limit hierarchy levels")
    merge_companies = fields.Boolean()
    show_hierarchy_level = fields.Integer("Hierarchy Levels to display", default=1)
    hide_parent_hierarchy_level = fields.Boolean(
        "Do not display parent levels", default=False
    )
    hide_account_at_0 = fields.Boolean(
        string="Hide accounts at 0",
        default=True,
        help="When this option is enabled, the trial balance will "
        "not display accounts that have initial balance = "
        "debit = credit = end balance = 0",
    )
    foreign_currency = fields.Boolean(
        string="Show foreign currency",
        help="Display foreign currency for move lines, unless "
        "account currency is not setup through chart of accounts "
        "will display initial and final balance in that currency.",
    )

    def _export(self, report_type):
        self.ensure_one()
        data = self._prepare_report_trial_balance()
        if report_type == "xlsx":
            report_name = "oxigen_account.report_trial_balance_consolidated_xlsx"
        else:
            report_name = "oxigen_account.report_trial_balance_consolidated"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(self, data=data)
        )

    def _prepare_report_trial_balance(self):
        self.ensure_one()
        fy_start_date = False
        for company in self.company_ids:
            date_from, date_to = date_utils.get_fiscal_year(
                self.date_from,
                day=company.fiscalyear_last_day,
                month=int(company.fiscalyear_last_month),
            )
            if not fy_start_date:
                fy_start_date = date_from
            elif fy_start_date != date_from:
                raise ValidationError(
                    _("You cannot select companies with different Fiscal Year Start")
                )
        return {
            "wizard_id": self.id,
            "company_ids": self.company_ids.ids,
            "date_from": self.date_from,
            "date_to": self.date_to,
            "fy_start_date": fy_start_date,
            "only_posted_moves": self.target_move == "posted",
            "foreign_currency": self.foreign_currency,
            "show_hierarchy": self.show_hierarchy,
            "limit_hierarchy_level": self.limit_hierarchy_level,
            "show_hierarchy_level": self.show_hierarchy_level,
            "hide_parent_hierarchy_level": self.hide_parent_hierarchy_level,
            "account_financial_report_lang": self.env.lang,
            "hide_account_at_0": self.hide_account_at_0,
            "merge_companies": self.merge_companies,
        }
