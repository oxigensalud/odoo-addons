# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemHazardResidualRisk(models.Model):
    _inherit = "mgmtsystem.hazard.residual_risk"

    usage_id = fields.Many2one(
        comodel_name="mgmtsystem.hazard.usage",
        string="Detectability",
    )
