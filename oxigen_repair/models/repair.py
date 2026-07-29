# Copyright 2022 ForgeFlow, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import float_is_zero


class RepairOrder(models.Model):
    _description = "Repair Order"
    _inherit = "repair.order"

    @api.model
    def _default_name(self):
        return self.env["ir.sequence"].next_by_code("repair.order")

    name = fields.Char(default=_default_name)
    distance_km = fields.Integer(string="Kilometers", aggregator="max")
    list_date = fields.Datetime(string="Lists date")
    # operations = fields.One2many(
    #     states={
    #         "draft": [("readonly", False)],
    #         "confirmed": [("readonly", False)],
    #         "under_repair": [("readonly", False)],
    #     }
    # )

    # fees_lines = fields.One2many(
    #     states={
    #         "draft": [("readonly", False)],
    #         "confirmed": [("readonly", False)],
    #         "under_repair": [("readonly", False)],
    #     }
    # )

    def action_repair_cancel_draft(self):
        """if MO in under_repair or cancelled states, it can be set again to draft"""

        if self.filtered(lambda repair: repair.state not in ["cancel", "under_repair"]):
            self.action_repair_cancel()
        sale_line_to_update = self.move_ids.sale_line_id.filtered(
            lambda line: line.order_id.state != "cancel"
            and float_is_zero(
                line.product_uom_qty, precision_rounding=line.product_uom.rounding
            )
        )
        sale_line_to_update.move_ids._update_repair_sale_order_line()
        self.move_ids.state = "draft"
        self.state = "draft"
        return True

    def unlink(self):
        for rec in self:
            if rec.state in ("done", "2binvoiced"):
                raise UserError(_("Cannot delete a finished Repair Order."))

        return super().unlink()

    @api.onchange("lot_id")
    def onchange_lot_id(self):
        if self.lot_id:
            ro = self.env["repair.order"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("lot_id", "=", self.lot_id.id),
                    ("state", "in", ("draft", "confirmed", "under_repair", "ready")),
                ],
                limit=1,
            )
            if ro:
                raise UserError(
                    _(
                        "Repair %(repair)s with lot %(lot)s of "
                        "product %(product)s must be finished before "
                        "creating a new Repair Order for the same lot."
                    )
                    % {
                        "repair": ro.name,
                        "lot": self.lot_id.name,
                        "product": self.product_id.name,
                    }
                )

    def copy(self, default=None):
        default = dict(default or {})
        default.update({"lot_id": ""})
        return super().copy(default)
