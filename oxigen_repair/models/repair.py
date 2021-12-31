# Copyright 2021 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, fields, models
from odoo.exceptions import UserError


class OxigenRepair(models.Model):
    _description = "Repair Order"
    _inherit = ["repair.order"]

    distance_km = fields.Integer(string="Kilometers", group_operator="max")
    list_date = fields.Datetime(string="Lists date")
    operations = fields.One2many(
        states={
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "under_repair": [("readonly", False)],
        }
    )

    fees_lines = fields.One2many(
        states={
            "draft": [("readonly", False)],
            "confirmed": [("readonly", False)],
            "under_repair": [("readonly", False)],
        }
    )

    def action_repair_cancel_draft(self):
        """ if MO in under_repair or cancelled states, it can be set again to draft"""

        if self.filtered(lambda repair: repair.state not in ["cancel", "under_repair"]):
            raise UserError(_("Repair must be canceled in order to reset it to draft."))
        self.mapped("operations").write({"state": "draft"})
        return self.write({"state": "draft"})

    def unlink(self):
        if self.state in ("done", "2binvoiced"):
            raise UserError(_("Cannot delete a finished Repair Order."))

        return super(OxigenRepair, self).unlink()
