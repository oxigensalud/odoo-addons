# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class FleetVehicle(models.Model):
    _inherit = "fleet.vehicle"

    transport_company_id = fields.Many2one(
        comodel_name="transport.company", string="Transport Company"
    )
    vehicle_identification = fields.Selection(
        selection=[
            ("van", "Van"),
            ("truck", "Truck"),
            ("tanker", "Tanker"),
        ]
    )
    is_shipping_vehicle = fields.Boolean(
        string="Shipping Vehicle",
        compute="_compute_is_shipping_vehicle",
        store=True,
        readonly=False,
    )

    @api.depends("transport_company_id")
    def _compute_is_shipping_vehicle(self):
        for vehicle in self:
            vehicle.is_shipping_vehicle = bool(vehicle.transport_company_id)
