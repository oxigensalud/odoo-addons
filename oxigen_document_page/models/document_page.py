# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import random

from odoo import _, api, fields, models
from odoo.exceptions import UserError

REFERENCE_MIN = 1
REFERENCE_MAX = 10**10 - 1
MAX_ATTEMPTS = 100


class DocumentPage(models.Model):
    _inherit = "document.page"

    active = fields.Boolean(tracking=True)

    @api.model
    def _generate_unique_reference(self):
        for _attempt in range(MAX_ATTEMPTS):
            candidate = "%010d" % random.randint(REFERENCE_MIN, REFERENCE_MAX)
            if not self.sudo().search_count([("reference", "=", candidate)]):
                return candidate
        raise UserError(
            _("Could not generate a unique 10-digit reference after %s attempts.")
            % MAX_ATTEMPTS
        )

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("reference"):
                vals["reference"] = self._generate_unique_reference()
        return super().create(vals_list)

    def _open_archive_wizard(self, archive_mode):
        active = self.filtered("active")
        inactive = self - active
        offending = inactive if archive_mode else active
        if offending:
            details = "\n".join(
                "- %s" % (r.reference and "%s - %s" % (r.reference, r.name) or r.name)
                for r in offending
            )
            if archive_mode:
                raise UserError(
                    _("Cannot archive document(s) that are already archived:\n%s")
                    % details
                )
            raise UserError(
                _("Cannot unarchive document(s) that are already active:\n%s") % details
            )
        records = active if archive_mode else inactive
        if not records:
            return False
        view = self.env.ref("oxigen_document_page.document_page_archive_wizard_form")
        return {
            "type": "ir.actions.act_window",
            "name": _("Archive") if archive_mode else _("Unarchive"),
            "res_model": "document.page.archive.wizard",
            "view_mode": "form",
            "view_id": view.id,
            "views": [(view.id, "form")],
            "target": "new",
            "context": {
                "default_document_page_ids": [(6, 0, records.ids)],
                "default_archive": archive_mode,
                "active_test": False,
            },
        }

    def action_archive(self):
        if self.env.context.get("archive_reason_provided"):
            return super().action_archive()
        return self._open_archive_wizard(archive_mode=True)

    def action_unarchive(self):
        if self.env.context.get("archive_reason_provided"):
            return super().action_unarchive()
        return self._open_archive_wizard(archive_mode=False)
