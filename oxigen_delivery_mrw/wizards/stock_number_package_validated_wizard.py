# Copyright 2022 ForgeFlow, S.L.
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>1
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import _, models
from odoo.exceptions import UserError


class StockNumberPackageValidateWiz(models.TransientModel):
    _inherit = "stock.number.package.validate.wizard"

    def mrw_send_shipping(self):
        if len(self.pick_ids) > 1:
            raise UserError(_("You cannot create more than one MRW shipping at a time"))
        self.pick_ids.write({"number_of_packages": self.number_of_packages})
        self.pick_ids.with_context(skip_mrw_immediate_wizard=True).button_validate()
        return True

    def process(self):
        return super(
            StockNumberPackageValidateWiz,
            self.with_context(skip_mrw_immediate_wizard=True),
        ).process()
