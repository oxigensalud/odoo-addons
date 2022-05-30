# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    # Override default value
    user_id = fields.Many2one(default=False)

    def request_validation(self):
        self.filtered(lambda r: not r.user_id).write({"user_id": self.env.uid})
        return super().request_validation()
