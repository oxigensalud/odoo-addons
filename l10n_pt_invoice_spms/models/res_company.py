# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    spms_certificate = fields.Binary(groups="base.group_system")
    spms_certificate_password = fields.Char(groups="base.group_system")
