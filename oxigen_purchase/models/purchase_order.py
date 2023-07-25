# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import api, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def request_validation(self):
        self.filtered(lambda r: not r.user_id).write({"user_id": self.env.uid})
        return super().request_validation()

    @api.model
    def _get_picking_type(self, company_id):
        user_warehouse = self.env.user.property_warehouse_id
        if user_warehouse:
            picking_type = self.env["stock.picking.type"].search(
                [("code", "=", "incoming"), ("warehouse_id", "=", user_warehouse.id)]
            )
            return picking_type[:1]
        else:
            return super()._get_picking_type(company_id)
