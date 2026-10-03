# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models

from ..hooks import MODULE


class BaseLanguageInstall(models.TransientModel):
    _inherit = "base.language.install"

    def lang_install(self):
        action = super().lang_install()
        # After the load, which installs the language and can leave the
        # dependencies' wording on the texts this module relabels, their
        # translations are put back as at install, by the system: the user
        # loading a language may have no rights on them
        self.env["ir.translation"].sudo()._force_module_terms(MODULE)
        return action
