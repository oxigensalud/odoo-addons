from odoo import models


class OxigenWizardUpdateChartsAccounts(models.TransientModel):

    _inherit = "wizard.update.charts.accounts"

    def _check_consistency(self):
        """Override method since we DON'T want to check the condition:
        - If a parent tax is tried to be created, children taxes must be
         also included to be created."""
