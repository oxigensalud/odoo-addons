from dateutil import relativedelta

from odoo import api, fields, models


class AccountUpdateLockDate(models.TransientModel):
    _inherit = "account.update.lock_date"

    show_change_date_msg = fields.Boolean(default=False)

    @api.model
    def default_get(self, field_list):
        res = super().default_get(field_list)
        fiscal_year = self.env.context.get("fiscalyear_lock_date", False)
        show_change_date_msg = self.env.context.get("show_change_date_msg", False)
        if fiscal_year and show_change_date_msg:
            res.update(
                {
                    "tax_lock_date": self.env.context.get("tax_lock_date", False),
                    "period_lock_date": self.env.context.get("period_lock_date", False),
                    "show_change_date_msg": True,
                    "fiscalyear_lock_date": fiscal_year,
                }
            )
        return res

    def show_unposted_entries(self):
        drafts = self.env["account.move"].search(
            [
                ("state", "=", "draft"),
                ("date", "<=", self.env.context["fiscalyear_lock_date"]),
            ]
        )
        return {
            "view_mode": "tree",
            "view_type": "tree",
            "name": "Unposted Entries",
            "res_model": "account.move",
            "type": "ir.actions.act_window",
            "domain": [("id", "in", drafts.ids)],
            "search_view_id": [
                self.env.ref("account.view_account_move_filter").id,
                "search",
            ],
            "views": [
                [self.env.ref("account.view_move_tree").id, "list"],
                [self.env.ref("account.view_move_form").id, "form"],
            ],
        }

    def change_drafts_date(self):
        self.fiscalyear_lock_date = self.env.context["fiscalyear_lock_date"]
        drafts = self.env["account.move"].search(
            [
                ("state", "=", "draft"),
                ("company_id", "=", self.env.company.id),
                ("date", "<=", self.fiscalyear_lock_date),
            ]
        )
        drafts.write(
            {
                "name": "/",
                "date": fields.Date.from_string(self.fiscalyear_lock_date)
                + relativedelta.relativedelta(days=1),
            }
        )
        view_id = self.env.ref(
            "account_lock_date_update.account_update_lock_date_form_view"
        ).id

        return {
            "name": "Update Draft Entries Date",
            "res_model": "account.update.lock_date",
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "views": [[view_id, "form"]],
            "target": "new",
            "context": {"show_change_date_msg": True},
        }
