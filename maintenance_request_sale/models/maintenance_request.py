# Copyright 2023 Dixmit
# # License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceRequest(models.Model):

    _inherit = "maintenance.request"

    sale_order_id = fields.Many2one(
        "sale.order", "Sale Order", groups="sales_team.group_sale_salesman"
    )
