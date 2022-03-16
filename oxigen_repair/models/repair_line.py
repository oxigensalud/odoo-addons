# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, models
from odoo.exceptions import UserError


class RepairLine(models.Model):
    _inherit = "repair.line"

    @api.onchange("repair_id", "product_id", "product_uom_qty")
    def onchange_product_id(self):
        if not self.repair_id.partner_id:
            raise UserError(_("Please select a Customer"))
        super(RepairLine, self).onchange_product_id()
