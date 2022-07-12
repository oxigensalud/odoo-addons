# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class ProductContainer(models.Model):
    _name = "product.container"
    _description = "Product Container"

    name = fields.Char(compute="_compute_name", store=True)
    container_type = fields.Selection(
        selection=[
            ("block", "Bloque"),
            ("bottle", "Botella"),
            ("compact_bottle", "Botella compacta"),
            ("compact_bottle_ac", "Botella compacta AC"),
            ("compact_bottle_al", "Botella compacta AL"),
            ("composite_bottle", "Botella compuesta"),
            ("pallet", "Palé"),
            ("tank", "Tanque"),
            ("heliums_tank", "Tanque Helios"),
        ],
        default="bottle",
    )
    liter_capacity = fields.Float(help="In Liters.")
    liter_capacity_str = fields.Char(compute="_compute_liter_capacity_str")
    extra_type = fields.Selection(
        selection=[
            ("tall", "Alta"),
            ("shor", "Baja"),
        ],
    )
    void_weight = fields.Float()

    @api.depends("liter_capacity")
    def _compute_liter_capacity_str(self):
        for container in self:
            if not container.liter_capacity:
                container.liter_capacity_str = "0"
                continue
            container.liter_capacity_str = (
                str(container.liter_capacity).rstrip("0").rstrip(".").replace(".", ",")
            )

    @api.depends("container_type", "liter_capacity", "extra_type")
    def _compute_name(self):
        for container in self:
            name = (
                (container.container_type or "")
                + " "
                + container.liter_capacity_str
                + " L"
            )
            if container.extra_type:
                name += " (" + container.extra_type + ")"
            container.name = name
