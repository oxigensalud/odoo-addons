# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models


class ContractContract(models.Model):
    _inherit = "contract.contract"

    def action_show_invoices(self):
        action = super().action_show_invoices()
        action["context"] = {"default_move_type": "contract"}
        return action
