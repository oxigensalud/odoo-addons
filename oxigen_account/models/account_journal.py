# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountJournal(models.Model):
    _inherit = "account.journal"

    # override domain in payment_debit_account_id and payment_credit_account_id:
    payment_debit_account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )
    payment_credit_account_id = fields.Many2one(
        domain="[('deprecated', '=', False), ('company_id', '=', company_id)]",
    )
