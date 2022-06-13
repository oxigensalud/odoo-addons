# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class Lead(models.Model):
    _inherit = "crm.lead"

    def _get_partner_email_update(self):
        self.ensure_one()
        if self.partner_id.name == "PRESUPUESTO GENÉRICO":
            return False
        return super()._get_partner_email_update()

    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.partner_id.name == "PRESUPUESTO GENÉRICO":
            return False
        return super()._get_partner_phone_update()
