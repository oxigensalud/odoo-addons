# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    def _check_orderpoint_picking_type(self):
        """
        We remove this warning.
        When the product has a reordering rule and this need triggers a transfer between
        warehouses + PO, dest_loc from orderpoint is from a different warehouse than
        warehouse_loc from the PO.
        """
