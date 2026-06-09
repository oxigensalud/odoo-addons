# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from ..hooks import apply_detectability_translations


class BaseLanguageInstall(models.TransientModel):
    _inherit = "base.language.install"

    def lang_install(self):
        action = super().lang_install()
        apply_detectability_translations(self.env, self.lang)
        return action
