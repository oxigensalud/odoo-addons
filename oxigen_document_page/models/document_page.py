# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import random

from odoo import _, api, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

REFERENCE_MIN = 10**9
REFERENCE_MAX = 10**10 - 1
MAX_ATTEMPTS = 100


class DocumentPage(models.Model):
    _inherit = "document.page"

    @api.model
    def _generate_unique_reference(self):
        for _attempt in range(MAX_ATTEMPTS):
            candidate = str(random.randint(REFERENCE_MIN, REFERENCE_MAX))
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
