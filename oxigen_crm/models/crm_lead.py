# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    is_generic_customer = fields.Boolean(
        compute="_compute_is_generic_customer",
    )

    @api.depends("partner_id")
    def _compute_is_generic_customer(self):
        generic_crm_customer_id = int(
            self.env["ir.config_parameter"].sudo().get_param("generic_crm_customer")
        )
        for rec in self:
            rec.is_generic_customer = rec.partner_id.id == generic_crm_customer_id

    def _get_partner_email_update(self):
        self.ensure_one()
        if self.is_generic_customer:
            return False
        return super()._get_partner_email_update()

    def _get_partner_phone_update(self):
        self.ensure_one()
        if self.is_generic_customer:
            return False
        return super()._get_partner_phone_update()
