# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AccountMoveLine(models.Model):

    _inherit = "account.move.line"

    spms_prescription = fields.Char()
    spms_user_number = fields.Char()
    spms_beneficiary_number = fields.Char()
    spms_start_date = fields.Date()
    spms_end_date = fields.Date()
    spms_suspension_reason_id = fields.Many2one(
        "spms.suspension.reason",
    )
    spms_context_id = fields.Many2one(
        "spms.context",
    )
    spms_prescription_type_id = fields.Many2one(
        "spms.prescription.type",
    )
    spms_send_invoice = fields.Boolean(related="partner_id.spms_send_invoice")

    def action_spms_send_invoice(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "l10n_pt_invoice_spms.spms_account_move_line_act_window"
        )
        action["res_id"] = self.id
        return action
