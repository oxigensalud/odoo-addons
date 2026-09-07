# Copyright 2022 ForgeFlow, S.L.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class OxigenRepair(models.Model):
    _description = "Repair Order"
    _inherit = ["repair.order"]

    @api.model
    def _default_name(self):
        if self._repair_reference_company().repair_reference_manual:
            return False
        return self.env["ir.sequence"].next_by_code("repair.order")

    name = fields.Char(default=_default_name)
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

    @api.model
    def _repair_reference_company(self, vals=None):
        """Company the repair order gets: the one in vals, else its default.

        The default of company_id is resolved the way the record will get it
        (context, ir.default, field default), not read from self.env.company.
        """
        company_id = (vals or {}).get("company_id") or self.default_get(
            ["company_id"]
        ).get("company_id")
        return self.env["res.company"].browse(company_id)

    @api.model
    def create(self, vals):
        # Core create() turns an empty or "/"-prefixed name into the next
        # sequence number: refuse it first when the company's reference is
        # manual. Write never numbers, so nothing else is needed.
        company = self._repair_reference_company(vals)
        name = vals.get("name")
        if company.repair_reference_manual and (not name or name.startswith("/")):
            raise ValidationError(
                _(
                    "The repair reference of company %s is manual: fill it in, "
                    "it is never assigned automatically."
                )
                % company.display_name
            )
        return super().create(vals)

    def action_repair_cancel_draft(self):
        """if MO in under_repair or cancelled states, it can be set again to draft"""

        if self.filtered(lambda repair: repair.state not in ["cancel", "under_repair"]):
            raise UserError(_("Repair must be canceled in order to reset it to draft."))
        self.mapped("operations").write({"state": "draft"})
        return self.write({"state": "draft"})

    def unlink(self):
        for rec in self:
            if rec.state in ("done", "2binvoiced"):
                raise UserError(_("Cannot delete a finished Repair Order."))

        return super(OxigenRepair, self).unlink()

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
                        "Repair %s with lot %s of product %s must be finished before "
                        "creating a new Repair Order for the same lot."
                    )
                    % (ro.name, self.lot_id.name, self.product_id.name)
                )

    def copy(self, default=None):
        default = dict(default or {})
        default.update({"lot_id": ""})
        return super(OxigenRepair, self).copy(default)
