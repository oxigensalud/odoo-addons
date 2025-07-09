# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SpmsLot(models.Model):

    _name = "spms.lot"
    _description = "SPMS Lot"

    name = fields.Char(required=True)
    lot_type = fields.Selection(
        [
            ("991", "Aerossolterapia"),
            ("992", "Oxigenoterapia"),
            ("993", "Ventiloterapia"),
            ("994", "Outros"),
        ],
        required=True,
        default="992",
    )
    _sql_constraints = [
        ("name_uniq", "unique(name)", "The name of the lot must be unique."),
    ]
