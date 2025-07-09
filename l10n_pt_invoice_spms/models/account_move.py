# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMove(models.Model):

    _inherit = "account.move"
    spms_send_invoice = fields.Boolean(related="partner_id.spms_send_invoice")
