# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class WizCandidatePicking(models.TransientModel):
    _inherit = "wiz.candidate.picking"

    do_show_action_confirm = fields.Boolean(compute="_compute_do_show_action_confirm")

    @api.depends("picking_id", "picking_id.move_lines")
    def _compute_do_show_action_confirm(self):
        for rec in self:
            options = self.wiz_barcode_id.option_group_id
            picking = rec.picking_id or self.env["stock.picking"].browse(
                self.env.context.get("picking_id", False)
            )
            if (
                picking.move_lines
                and picking.state == "draft"
                and options
                and options.barcode_guided_mode != "guided"
            ):
                rec.do_show_action_confirm = True
            else:
                rec.do_show_action_confirm = False

    def action_confirm_picking(self):
        picking = self.env["stock.picking"].browse(
            self.env.context.get("picking_id", False)
        )
        picking.action_confirm()
        return self.action_validate_picking()
