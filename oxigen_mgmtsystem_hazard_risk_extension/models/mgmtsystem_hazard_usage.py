# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemHazardUsage(models.Model):
    _inherit = "mgmtsystem.hazard.usage"

    name = fields.Char(
        string="Detectability",
        required=True,
        translate=True,
    )
