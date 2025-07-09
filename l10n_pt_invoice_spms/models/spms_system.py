# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SpmsSystem(models.Model):

    _name = "spms.system"
    _description = "Spms System"  # TODO

    code = fields.Char(required=True)
    name = fields.Char()
    unit_price = fields.Float()
    contract_number = fields.Char()
    lot_id = fields.Many2one("spms.lot")

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The code must be unique"),
    ]
