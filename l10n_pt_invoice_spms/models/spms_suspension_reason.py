# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SpmsSuspensionReason(models.Model):

    _name = "spms.suspension.reason"
    _description = "SPMS Suspension Reason"

    code = fields.Char(required=True)
    name = fields.Char()

    _sql_constraints = [
        ("code_uniq", "unique(code)", "The code must be unique"),
    ]
