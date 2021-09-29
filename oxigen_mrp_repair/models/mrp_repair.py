# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class OxigenRepair(models.Model):
    _description = "Repair Order"
    _inherit = ["mrp.repair"]

    operations = fields.One2many(
        states={
            "2binvoiced": [("readonly", False)],
            "under_repair": [("readonly", False)],
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "ready": [("readonly", False)],
        }
    )
    fees_lines = fields.One2many(
        states={
            "2binvoiced": [("readonly", False)],
            "under_repair": [("readonly", False)],
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "ready": [("readonly", False)],
        }
    )
