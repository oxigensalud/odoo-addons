# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class DocumentPageArchiveWizard(models.TransientModel):
    _name = "document.page.archive.wizard"
    _description = "Archive or unarchive document pages with reason"

    document_page_ids = fields.Many2many(
        "document.page",
        required=True,
        string="Document Pages",
    )
    archive = fields.Boolean(
        default=True,
        string="Archive",
        help="True when the wizard archives the documents; "
        "False when it unarchives them.",
    )
    reason = fields.Text(
        required=True,
        string="Reason",
        help="Reason for archiving or unarchiving. Will be logged in the "
        "chatter of each affected document for traceability.",
    )

    def action_confirm(self):
        self.ensure_one()
        pages = self.with_context(active_test=False).document_page_ids
        new_active = not self.archive
        action_label = _("archived") if self.archive else _("unarchived")
        pages.with_context(
            archive_reason_provided=True,
            tracking_disable=True,
        ).write({"active": new_active})
        body_template = _(
            "<strong>Document %(action)s.</strong><br/>"
            "<strong>Reason:</strong> %(reason)s"
        )
        for doc in pages:
            doc.message_post(
                body=body_template % {"action": action_label, "reason": self.reason},
                subtype_xmlid="mail.mt_note",
            )
        return {"type": "ir.actions.act_window_close"}
