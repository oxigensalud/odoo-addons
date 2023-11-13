# Copyright Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models
from odoo.osv import expression


class AccountAsset(models.Model):
    _inherit = "account.asset"

    def _active_capital_asset_prorate_regularization_domain(self):
        return expression.OR(
            [
                super()._active_capital_asset_prorate_regularization_domain,
                [("mod322_id", "=", False)][
                    ("mod322_id.state", "in", ["posted", "done"]),
                ],
            ]
        )
