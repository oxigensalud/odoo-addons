# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class StockPicking(models.Model):
    _inherit = "stock.picking"

    transport_company_id = fields.Many2one(
        comodel_name="transport.company", string="Transport Company"
    )
    transport_shipper_id = fields.Many2one(
        comodel_name="transport.shipper",
        string="Shipper",
        domain="[('transport_company_id', '=', transport_company_id)]",
    )
    transport_vehicle_id = fields.Many2one(
        comodel_name="fleet.vehicle",
        string="Vehicle",
        domain="[('transport_company_id', '=', transport_company_id)]",
    )
    has_gases = fields.Boolean(compute="_compute_has_gases")

    @api.depends("move_lines.product_id.is_gas")
    def _compute_has_gases(self):
        for picking in self:
            has_gases = picking.move_lines.mapped("product_id.is_gas")
            if isinstance(has_gases, bool):
                has_gases = [has_gases]
            picking.has_gases = any(has_gases)
