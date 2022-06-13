# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class Lead(models.Model):
    _inherit = "crm.lead"

    is_generic_customer = fields.Boolean(
        compute="_compute_is_generic_customer",
    )

    @api.depends("partner_id")
    def _compute_is_generic_customer(self):
        generic_crm_customer_param = (
            self.env["ir.config_parameter"].sudo().get_param("generic_crm_customer")
        )
        if all(c in generic_crm_customer_param for c in ["[", ",", "]"]):
            generic_crm_customer_ids = safe_eval(generic_crm_customer_param)
        else:
            generic_crm_customer_ids = [int(generic_crm_customer_param)]
        for rec in self:
            rec.is_generic_customer = rec.partner_id.id in generic_crm_customer_ids

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
