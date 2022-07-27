# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    oxigen_margin_percent = fields.Float(
        "Margin (%)",
        compute="_compute_oxigen_margin_percent",
        store=True,
        groups="base.group_user",
        group_operator="avg",
        help="Custom %Margin calculated as Margin/Cost",
    )

    @api.depends("price_subtotal", "product_uom_qty", "purchase_price")
    def _compute_oxigen_margin_percent(self):
        # In odoo, margin_percent is calculated as line.margin/line.price_subtotal
        # Oxigen wants this % calculated with purchase_price(cost)
        for line in self:
            line.oxigen_margin_percent = line.purchase_price and line.margin / (
                line.purchase_price * line.product_uom_qty
            )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    oxigen_margin_percent = fields.Float(
        "Margin (%)", compute="_compute_oxigen_margin_percent", store=True
    )

    total_purchase_price = fields.Float(
        compute="_compute_oxigen_margin_percent", store=True
    )

    @api.depends("order_line.margin", "amount_untaxed")
    def _compute_oxigen_margin_percent(self):
        for order in self:
            order.total_purchase_price = sum(
                [
                    line.purchase_price * line.product_uom_qty
                    for line in order.order_line
                ]
            )
            order.oxigen_margin_percent = (
                order.total_purchase_price and order.margin / order.total_purchase_price
            )
