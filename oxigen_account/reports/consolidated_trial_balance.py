# Copyright 2020 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.tools.float_utils import float_is_zero


class TrialBalanceConsolidatedReport(models.AbstractModel):
    _name = "report.oxigen_account.report_trial_balance_consolidated"
    _description = "Consolidated Trial Balance Report"
    _inherit = "report.account_financial_report.abstract_report"

    def _get_initial_balances_bs_ml_domain(
        self,
        accounts,
        companies,
        date_from,
        only_posted_moves,
        fy_start_date,
    ):
        accounts_domain = [
            ("id", "in", accounts.ids),
            ("user_type_id.include_initial_balance", "=", True),
        ]
        domain = [("date", "<", date_from)]
        domain += [
            (
                "account_id",
                "in",
                self.env["account.account"].search(accounts_domain).ids,
            )
        ]
        domain += [("company_id", "in", companies.ids)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        return domain

    def _get_initial_balances_pl_ml_domain(
        self,
        accounts,
        companies,
        date_from,
        only_posted_moves,
        fy_start_date,
    ):
        accounts_domain = [
            ("id", "in", accounts.ids),
            ("user_type_id.include_initial_balance", "=", False),
        ]
        domain = [("date", "<", date_from), ("date", ">=", fy_start_date)]
        domain += [
            (
                "account_id",
                "in",
                self.env["account.account"].search(accounts_domain).ids,
            )
        ]
        domain += [("company_id", "in", companies.ids)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        return domain

    @api.model
    def _get_period_ml_domain(
        self,
        accounts,
        companies,
        date_to,
        date_from,
        only_posted_moves,
    ):
        domain = [
            ("display_type", "=", False),
            ("date", ">=", date_from),
            ("date", "<=", date_to),
        ]
        domain += [("company_id", "in", companies.ids)]
        domain += [("account_id", "in", accounts.ids)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        return domain

    @api.model
    def _prepare_total_amount(self, tb, foreign_currency):
        res = {
            "credit": 0.0,
            "debit": 0.0,
            "balance": 0.0,
            "initial_balance": tb["balance"],
            "ending_balance": tb["balance"],
        }
        if foreign_currency:
            res["initial_currency_balance"] = round(tb["amount_currency"], 2)
            res["ending_currency_balance"] = round(tb["amount_currency"], 2)
        return res

    @api.model
    def _compute_account_amount(
        self, total_amount, tb_initial_acc, tb_period_acc, foreign_currency
    ):
        for tb in tb_period_acc:
            acc_id = tb["account_id"][0]
            total_amount[acc_id] = self._prepare_total_amount(tb, foreign_currency)
            total_amount[acc_id]["credit"] = tb["credit"]
            total_amount[acc_id]["debit"] = tb["debit"]
            total_amount[acc_id]["balance"] = tb["balance"]
            total_amount[acc_id]["initial_balance"] = 0.0
        for tb in tb_initial_acc:
            acc_id = tb["account_id"]
            if acc_id not in total_amount.keys():
                total_amount[acc_id] = self._prepare_total_amount(tb, foreign_currency)
            else:
                total_amount[acc_id]["initial_balance"] = tb["balance"]
                total_amount[acc_id]["ending_balance"] += tb["balance"]
                if foreign_currency:
                    total_amount[acc_id]["initial_currency_balance"] = round(
                        tb["amount_currency"], 2
                    )
                    total_amount[acc_id]["ending_currency_balance"] += round(
                        tb["amount_currency"], 2
                    )
        return total_amount

    def _get_initial_balance_fy_pl_ml_domain(
        self,
        accounts,
        company_id,
        fy_start_date,
        only_posted_moves,
    ):
        accounts_domain = [
            ("company_id", "=", company_id),
            ("user_type_id.include_initial_balance", "=", False),
        ]
        accounts_domain += [("id", "in", accounts.ids)]
        domain = [("date", "<", fy_start_date)]
        domain += [
            (
                "account_id",
                "in",
                self.env["account.account"].search(accounts_domain).ids,
            )
        ]
        domain += [("company_id", "=", company_id)]
        if only_posted_moves:
            domain += [("move_id.state", "=", "posted")]
        else:
            domain += [("move_id.state", "in", ["posted", "draft"])]
        return domain

    def _get_pl_initial_balance(
        self,
        accounts,
        company_id,
        fy_start_date,
        only_posted_moves,
        foreign_currency,
    ):
        domain = self._get_initial_balance_fy_pl_ml_domain(
            accounts,
            company_id,
            fy_start_date,
            only_posted_moves,
        )
        initial_balances = self.env["account.move.line"].read_group(
            domain=domain,
            fields=["account_id", "balance", "amount_currency"],
            groupby=["account_id"],
        )
        pl_initial_balance = 0.0
        pl_initial_currency_balance = 0.0
        for initial_balance in initial_balances:
            pl_initial_balance += initial_balance["balance"]
            if foreign_currency:
                pl_initial_currency_balance += round(
                    initial_balance["amount_currency"], 2
                )
        return pl_initial_balance, pl_initial_currency_balance

    def _remove_accounts_at_cero(self, total_amount, companies):
        currency = companies.mapped("currency_id")
        if len(currency) != 1:
            raise ValidationError(_("Only one currency is allowed"))

        def is_removable(d):
            rounding = currency.rounding
            return (
                float_is_zero(d["initial_balance"], precision_rounding=rounding)
                and float_is_zero(d["credit"], precision_rounding=rounding)
                and float_is_zero(d["debit"], precision_rounding=rounding)
                and float_is_zero(d["ending_balance"], precision_rounding=rounding)
            )

        accounts_to_remove = []
        for acc_id, ta_data in total_amount.items():
            if is_removable(ta_data):
                accounts_to_remove.append(acc_id)
        for account_id in accounts_to_remove:
            del total_amount[account_id]

    def _get_hierarchy_groups(self, group_ids, groups_data, foreign_currency):
        for group_id in group_ids:
            parent_id = groups_data[group_id]["parent_id"]
            while parent_id:
                if parent_id not in groups_data.keys():
                    group = self.env["account.group"].browse(parent_id)
                    groups_data[group.id] = {
                        "id": group.id,
                        "code": group.code_prefix_start,
                        "name": group.name,
                        "parent_id": group.parent_id.id,
                        "company": group.company_id.name,
                        "parent_path": group.parent_path,
                        "complete_code": group.complete_code,
                        "account_ids": group.compute_account_ids.ids,
                        "type": "group_type",
                        "initial_balance": 0,
                        "debit": 0,
                        "credit": 0,
                        "balance": 0,
                        "ending_balance": 0,
                    }
                    if foreign_currency:
                        groups_data[group.id].update(
                            initial_currency_balance=0,
                            ending_currency_balance=0,
                        )
                acc_keys = ["debit", "credit", "balance"]
                acc_keys += ["initial_balance", "ending_balance"]
                for acc_key in acc_keys:
                    groups_data[parent_id][acc_key] += groups_data[group_id][acc_key]
                if foreign_currency:
                    groups_data[group_id]["initial_currency_balance"] += groups_data[
                        group_id
                    ]["initial_currency_balance"]
                    groups_data[group_id]["ending_currency_balance"] += groups_data[
                        group_id
                    ]["ending_currency_balance"]
                parent_id = groups_data[parent_id]["parent_id"]
        return groups_data

    def _get_groups_data(
        self, accounts_data, total_amount, foreign_currency, merge_companies
    ):
        accounts_ids = list(accounts_data.keys())
        accounts = self.env["account.account"].browse(accounts_ids)
        account_group_relation = {}
        for account in accounts:
            accounts_data[account.id]["complete_code"] = (
                account.group_id.complete_code + " / " + account.code
                if account.group_id.id
                else ""
            )
            if account.group_id.id:
                if account.group_id.id not in account_group_relation.keys():
                    account_group_relation.update({account.group_id.id: [account.id]})
                else:
                    account_group_relation[account.group_id.id].append(account.id)
        groups = self.env["account.group"].browse(account_group_relation.keys())
        groups_data = {}
        for group in groups:
            groups_data.update(
                {
                    group.id: {
                        "id": group.id,
                        "code": group.code_prefix_start,
                        "name": group.name,
                        "parent_id": group.parent_id.id,
                        "parent_path": group.parent_path,
                        "company": group.company_id.name,
                        "type": "group_type",
                        "complete_code": group.complete_code,
                        "account_ids": group.compute_account_ids.ids,
                        "initial_balance": 0.0,
                        "credit": 0.0,
                        "debit": 0.0,
                        "balance": 0.0,
                        "ending_balance": 0.0,
                    }
                }
            )
            if foreign_currency:
                groups_data[group.id]["initial_currency_balance"] = 0.0
                groups_data[group.id]["ending_currency_balance"] = 0.0
        for group_id in account_group_relation.keys():
            for account_id in account_group_relation[group_id]:
                groups_data[group_id]["initial_balance"] += total_amount[account_id][
                    "initial_balance"
                ]
                groups_data[group_id]["debit"] += total_amount[account_id]["debit"]
                groups_data[group_id]["credit"] += total_amount[account_id]["credit"]
                groups_data[group_id]["balance"] += total_amount[account_id]["balance"]
                groups_data[group_id]["ending_balance"] += total_amount[account_id][
                    "ending_balance"
                ]
                if foreign_currency:
                    groups_data[group_id]["initial_currency_balance"] += total_amount[
                        account_id
                    ]["initial_currency_balance"]
                    groups_data[group_id]["ending_currency_balance"] += total_amount[
                        account_id
                    ]["ending_currency_balance"]
        group_ids = list(groups_data.keys())
        groups_data = self._get_hierarchy_groups(
            group_ids,
            groups_data,
            foreign_currency,
        )

        return self._merge_data(groups_data, foreign_currency, merge_companies)

    def _merge_data(self, original_data, foreign_currency, merge_companies):
        if not merge_companies:
            return original_data
        new_data = {}
        for data in original_data.values():
            if data["code"] not in new_data:
                new_data[data["code"]] = data.copy()
                continue
            acc_keys = ["debit", "credit", "balance"]
            acc_keys += ["initial_balance", "ending_balance"]
            for acc_key in acc_keys:
                new_data[data["code"]][acc_key] += data[acc_key]
            if foreign_currency:
                new_data[data["code"]]["initial_currency_balance"] += data[
                    "initial_currency_balance"
                ]
                new_data[data["code"]]["ending_currency_balance"] += data[
                    "ending_currency_balance"
                ]
        return new_data

    @api.model
    def _get_data(
        self,
        companies,
        date_to,
        date_from,
        foreign_currency,
        only_posted_moves,
        fy_start_date,
        hide_account_at_0,
    ):
        accounts = self.env["account.account"].search(
            [("company_id", "in", companies.ids)]
        )
        tb_initial_acc = []
        for account in accounts:
            tb_initial_acc.append(
                {"account_id": account.id, "balance": 0.0, "amount_currency": 0.0}
            )
        initial_domain_bs = self._get_initial_balances_bs_ml_domain(
            accounts,
            companies,
            date_from,
            only_posted_moves,
            fy_start_date,
        )
        tb_initial_acc_bs = self.env["account.move.line"].read_group(
            domain=initial_domain_bs,
            fields=["account_id", "balance", "amount_currency"],
            groupby=["account_id"],
        )
        initial_domain_pl = self._get_initial_balances_pl_ml_domain(
            accounts,
            companies,
            date_from,
            only_posted_moves,
            fy_start_date,
        )
        tb_initial_acc_pl = self.env["account.move.line"].read_group(
            domain=initial_domain_pl,
            fields=["account_id", "balance", "amount_currency"],
            groupby=["account_id"],
        )
        tb_initial_acc_rg = tb_initial_acc_bs + tb_initial_acc_pl
        for account_rg in tb_initial_acc_rg:
            element = list(
                filter(
                    lambda acc_dict: acc_dict["account_id"]
                    == account_rg["account_id"][0],
                    tb_initial_acc,
                )
            )
            if element:
                element[0]["balance"] += account_rg["balance"]
                element[0]["amount_currency"] += account_rg["amount_currency"]
        if hide_account_at_0:
            tb_initial_acc = [p for p in tb_initial_acc if p["balance"] != 0]
        period_domain = self._get_period_ml_domain(
            accounts,
            companies,
            date_to,
            date_from,
            only_posted_moves,
        )
        tb_period_acc = self.env["account.move.line"].read_group(
            domain=period_domain,
            fields=["account_id", "debit", "credit", "balance", "amount_currency"],
            groupby=["account_id"],
        )
        total_amount = {}
        total_amount = self._compute_account_amount(
            total_amount, tb_initial_acc, tb_period_acc, foreign_currency
        )
        # Remove accounts a 0 from collections
        if hide_account_at_0:
            self._remove_accounts_at_cero(total_amount, companies)
        accounts_ids = list(total_amount.keys())
        account_type = self.env.ref("account.data_unaffected_earnings")
        for company in companies:
            unaffected_earnings_account = self.env["account.account"].search(
                [
                    ("user_type_id", "=", account_type.id),
                    ("company_id", "=", company.id),
                ]
            )
            if len(unaffected_earnings_account) != 1:
                raise ValidationError(
                    _("Only one earnings account is expected for company")
                )
            unaffected_id = unaffected_earnings_account.id
            (
                pl_initial_balance,
                pl_initial_currency_balance,
            ) = self._get_pl_initial_balance(
                accounts,
                company.id,
                fy_start_date,
                only_posted_moves,
                foreign_currency,
            )
            if unaffected_id:
                if unaffected_id not in accounts_ids:
                    accounts_ids.append(unaffected_id)
                    total_amount[unaffected_id] = {}
                    total_amount[unaffected_id]["initial_balance"] = 0.0
                    total_amount[unaffected_id]["balance"] = 0.0
                    total_amount[unaffected_id]["credit"] = 0.0
                    total_amount[unaffected_id]["debit"] = 0.0
                    total_amount[unaffected_id]["ending_balance"] = 0.0
                    if foreign_currency:
                        total_amount[unaffected_id]["initial_currency_balance"] = 0.0
                        total_amount[unaffected_id]["ending_currency_balance"] = 0.0
                total_amount[unaffected_id]["ending_balance"] += pl_initial_balance
                total_amount[unaffected_id]["initial_balance"] += pl_initial_balance
                if foreign_currency:
                    total_amount[unaffected_id][
                        "ending_currency_balance"
                    ] += pl_initial_currency_balance
                    total_amount[unaffected_id][
                        "initial_currency_balance"
                    ] += pl_initial_currency_balance

        accounts_data = self._get_accounts_data(accounts_ids)
        return total_amount, accounts_data

    def _get_accounts_data(self, account_ids):
        accounts_data = super()._get_accounts_data(account_ids)
        for account_id in accounts_data:
            accounts_data[account_id].update(
                {
                    "company": self.env["account.account"]
                    .browse(account_id)
                    .company_id.name
                }
            )
        return accounts_data

    def _get_report_values(self, docids, data):
        wizard_id = data["wizard_id"]
        companies = self.env["res.company"].browse(data["company_ids"])
        date_to = data["date_to"]
        date_from = data["date_from"]
        show_hierarchy = data["show_hierarchy"]
        show_hierarchy_level = data["show_hierarchy_level"]
        foreign_currency = data["foreign_currency"]
        only_posted_moves = data["only_posted_moves"]
        fy_start_date = data["fy_start_date"]
        hide_account_at_0 = data["hide_account_at_0"]
        merge_companies = data["merge_companies"]
        total_amount, accounts_data = self._get_data(
            companies,
            date_to,
            date_from,
            foreign_currency,
            only_posted_moves,
            fy_start_date,
            hide_account_at_0,
        )
        trial_balance = []

        for account_id in accounts_data.keys():
            accounts_data[account_id].update(
                {
                    "initial_balance": total_amount[account_id]["initial_balance"],
                    "credit": total_amount[account_id]["credit"],
                    "debit": total_amount[account_id]["debit"],
                    "balance": total_amount[account_id]["balance"],
                    "ending_balance": total_amount[account_id]["ending_balance"],
                    "type": "account_type",
                }
            )
            if foreign_currency:
                accounts_data[account_id].update(
                    {
                        "ending_currency_balance": total_amount[account_id][
                            "ending_currency_balance"
                        ],
                        "initial_currency_balance": total_amount[account_id][
                            "initial_currency_balance"
                        ],
                    }
                )
        if show_hierarchy:
            groups_data = self._get_groups_data(
                accounts_data, total_amount, foreign_currency, merge_companies
            )
            trial_balance = list(groups_data.values())
            trial_balance += list(
                self._merge_data(
                    accounts_data, foreign_currency, merge_companies
                ).values()
            )
            trial_balance = sorted(trial_balance, key=lambda k: k["complete_code"])
            for trial in trial_balance:
                counter = trial["complete_code"].count("/")
                trial["level"] = counter
        else:
            trial_balance = list(
                self._merge_data(
                    accounts_data, foreign_currency, merge_companies
                ).values()
            )
            trial_balance = sorted(trial_balance, key=lambda k: k["code"])
        accounts_data = self._merge_data(
            accounts_data, foreign_currency, merge_companies
        )
        return {
            "doc_ids": [wizard_id],
            "doc_model": "trial.balance.multicompany.report.wizard",
            "docs": self.env["trial.balance.multicompany.report.wizard"].browse(
                wizard_id
            ),
            "foreign_currency": data["foreign_currency"],
            "date_from": data["date_from"],
            "date_to": data["date_to"],
            "only_posted_moves": data["only_posted_moves"],
            "limit_hierarchy_level": data["limit_hierarchy_level"],
            "show_hierarchy": show_hierarchy,
            "hide_parent_hierarchy_level": data["hide_parent_hierarchy_level"],
            "trial_balance": trial_balance,
            "total_amount": total_amount,
            "accounts_data": accounts_data,
            "show_hierarchy_level": show_hierarchy_level,
            "currency_model": self.env["res.currency"],
            "merge_companies": merge_companies,
        }
