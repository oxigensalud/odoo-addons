# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _render_csv(self, report_ref, docids, data):
        if docids is None:
            docids = []
        return super()._render_csv(report_ref, docids, data)

