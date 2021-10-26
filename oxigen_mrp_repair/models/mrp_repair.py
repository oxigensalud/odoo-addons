# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class OxigenRepair(models.Model):
    _description = "Repair Order"
    _inherit = ["mrp.repair"]

    operations = fields.One2many(
        states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]}
    )
    fees_lines = fields.One2many(
        states={"draft": [("readonly", False)], "confirmed": [("readonly", False)]}
    )

    @api.multi
    def action_repair_cancel_draft(self):
        if self.filtered(lambda repair: repair.state not in ["cancel", "under_repair"]):
            raise UserError(_("Repair must be canceled in order to reset it to draft."))
        self.mapped("operations").write({"state": "draft"})
        return self.write({"state": "draft"})
