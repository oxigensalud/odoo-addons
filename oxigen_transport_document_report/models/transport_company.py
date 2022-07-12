# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class TransportCompany(models.Model):
    _name = "transport.company"
    _description = "Transport Company"
    _inherits = {"res.partner": "partner_id"}

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        required=True,
        domain="['|', ('parent_id','=', False), ('is_company','=', True)]",
        ondelete="cascade",
        string="Partner",
        auto_join=True,
    )
    shipper_ids = fields.One2many(
        comodel_name="transport.shipper",
        inverse_name="transport_company_id",
        string="Shippers",
    )
    vehicle_ids = fields.One2many(
        comodel_name="fleet.vehicle",
        inverse_name="transport_company_id",
        string="Vehicles",
        domain="[('is_shipping_vehicle', '=', True)]",
    )
