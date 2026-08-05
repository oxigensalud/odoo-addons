# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class AccountPaymentMethodLine(models.Model):
    _inherit = "account.payment.method.line"

    payment_account_id = fields.Many2one(
        comodel_name="account.account",
        domain="[('deprecated', '=', False)]",
    )
