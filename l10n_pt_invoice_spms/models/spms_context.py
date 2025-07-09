# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SpmsContext(models.Model):

    _name = "spms.context"

    code = fields.Char(required=True)
    name = fields.Char()

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The code must be unique"),
    ]
