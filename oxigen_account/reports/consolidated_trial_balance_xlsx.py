# Copyright 2020 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models


class TrialBalanceConsolidatedReport(models.AbstractModel):
    _name = "report.oxigen_account.report_trial_balance_consolidated_xlsx"
    _description = "Consolidated Trial Balance Report XLSX"
    _inherit = "report.account_financial_report.abstract_report_xlsx"

    def _get_report_name(self, report, data=False):
        return _("Trial Balance")

    def _add_column(self, res, col, col_number):
        res[col_number] = col
        return col_number + 1

    def _get_report_columns(self, report):
        col_number = 0
        res = {}
        for col in [
            {"header": _("Code"), "field": "code", "width": 10},
            {"header": _("Account"), "field": "name", "width": 60},
        ]:
            col_number = self._add_column(res, col, col_number)
        if not report.merge_companies:
            col_number = self._add_column(
                res,
                {"header": _("Company"), "field": "company", "width": 40},
                col_number,
            )
        for col in [
            {
                "header": _("Initial balance"),
                "field": "initial_balance",
                "type": "amount",
                "width": 14,
            },
            {
                "header": _("Debit"),
                "field": "debit",
                "type": "amount",
                "width": 14,
            },
            {
                "header": _("Credit"),
                "field": "credit",
                "type": "amount",
                "width": 14,
            },
            {
                "header": _("Ending balance"),
                "field": "ending_balance",
                "type": "amount",
                "width": 14,
            },
        ]:
            col_number = self._add_column(res, col, col_number)
        if report.foreign_currency:
            col_number = self._add_column(
                res,
                {
                    "header": _("Initial balance"),
                    "field": "initial_currency_balance",
                    "type": "amount_currency",
                    "width": 14,
                },
                col_number,
            )
            col_number = self._add_column(
                res,
                {
                    "header": _("Ending balance"),
                    "field": "ending_currency_balance",
                    "type": "amount_currency",
                    "width": 14,
                },
                col_number,
            )
        return res

    def _get_report_filters(self, report):
        return [
            [
                _("Date range filter"),
                _("From: %s To: %s") % (report.date_from, report.date_to),
            ],
            [
                _("Target moves filter"),
                _("All posted entries")
                if report.target_move == "posted"
                else _("All entries"),
            ],
            [
                _("Account at 0 filter"),
                _("Hide") if report.hide_account_at_0 else _("Show"),
            ],
            [
                _("Show foreign currency"),
                _("Yes") if report.foreign_currency else _("No"),
            ],
            [
                _("Limit hierarchy levels"),
                _("Level %s" % report.show_hierarchy_level)
                if report.limit_hierarchy_level
                else _("No limit"),
            ],
        ]

    def _get_col_count_filter_name(self):
        return 2

    def _get_col_count_filter_value(self):
        return 3

    def _generate_report_content(self, workbook, report, data, report_data):
        res_data = self.env[
            "report.oxigen_account.report_trial_balance_consolidated"
        ]._get_report_values(report, data)
        trial_balance = res_data["trial_balance"]
        show_hierarchy = res_data["show_hierarchy"]
        show_hierarchy_level = res_data["show_hierarchy_level"]
        limit_hierarchy_level = res_data["limit_hierarchy_level"]
        hide_parent_hierarchy_level = res_data["hide_parent_hierarchy_level"]
        self.write_array_header(report_data)
        # For each account
        for balance in trial_balance:
            if show_hierarchy:
                if limit_hierarchy_level:
                    if show_hierarchy_level > balance["level"] and (
                        not hide_parent_hierarchy_level
                        or (show_hierarchy_level - 1) == balance["level"]
                    ):
                        # Display account lines
                        self.write_line_from_dict(balance, report_data)
                else:
                    self.write_line_from_dict(balance, report_data)
            else:
                self.write_line_from_dict(balance, report_data)

    def write_line(self, line_object, type_object, report_data):
        """Write a line on current line using all defined columns field name.
        Columns are defined with `_get_report_columns` method.
        """
        if type_object == "partner":
            line_object.currency_id = line_object.report_account_id.currency_id
        elif type_object == "account":
            line_object.currency_id = line_object.currency_id
        super().write_line(line_object, report_data)
