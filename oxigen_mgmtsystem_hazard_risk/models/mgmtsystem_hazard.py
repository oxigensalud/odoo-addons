# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MgmtsystemHazard(models.Model):
    _inherit = "mgmtsystem.hazard"

    usage_id = fields.Many2one(
        comodel_name="mgmtsystem.hazard.usage",
        string="Detectability",
    )


class MgmtsystemHazardUsage(models.Model):
    _inherit = "mgmtsystem.hazard.usage"

    name = fields.Char(
        string="Detectability",
        required=True,
        translate=True,
    )


class MgmtsystemHazardResidualRisk(models.Model):
    _inherit = "mgmtsystem.hazard.residual_risk"

    usage_id = fields.Many2one(
        comodel_name="mgmtsystem.hazard.usage",
        string="Detectability",
    )


class MgmtsystemHazardRiskComputation(models.Model):
    _inherit = "mgmtsystem.hazard.risk.computation"

    # Minimal technical enabler for translating visible formula descriptions.
    description = fields.Text(translate=True)
