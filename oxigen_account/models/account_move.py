# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class AccountMove(models.Model):
    _inherit = "account.move"

    @api.onchange("invoice_date")
    def _onchange_invoice_date(self):
        self.date = self.invoice_date

    @api.onchange("ref")
    def _onchange_ref(self):
        self.payment_reference = self.ref
