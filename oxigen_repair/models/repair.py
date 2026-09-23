# Copyright 2022 ForgeFlow, S.L.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class RepairOrder(models.Model):
    _description = "Repair Order"
    _inherit = "repair.order"

    name = fields.Char(readonly=False)
    repair_reference_manual = fields.Boolean(
        related="company_id.repair_reference_manual"
    )
    distance_km = fields.Integer(string="Kilometers", aggregator="max")
    list_date = fields.Datetime(string="Lists date")

    @api.depends("product_location_src_id")
    def _compute_product_location_dest_id(self):
        for repair in self:
            repair.product_location_dest_id = repair.product_location_src_id

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
    def _repair_reference_placeholder(self):
        # The "New" the core defaults the reference to and replaces by the
        # sequence number in create(), in the language of the user.
        return self._fields["name"].default(self)

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        if (
            "name" in res
            and self._repair_reference_company(res).repair_reference_manual
        ):
            res["name"] = False
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # Core create() turns an empty or placeholder name into the next
        # number of the operation type sequence: refuse it first when the
        # company's reference is manual.
        placeholder = self._repair_reference_placeholder()
        for vals in vals_list:
            company = self._repair_reference_company(vals)
            name = vals.get("name")
            if company.repair_reference_manual and (not name or name == placeholder):
                raise ValidationError(
                    _(
                        "The repair reference of company %s is manual: fill it in, "
                        "it is never assigned automatically."
                    )
                    % company.display_name
                )
        return super().create(vals_list)

    def write(self, vals):
        manual_names = {}
        if vals.get("picking_type_id") and "name" not in vals:
            manual_names = {
                repair: repair.name
                for repair in self.filtered("repair_reference_manual")
            }
        res = super().write(vals)
        for repair, name in manual_names.items():
            if repair.name != name:
                repair.name = name
        return res

    def unlink(self):
        for rec in self:
            if rec.state == "done":
                raise UserError(_("Cannot delete a finished Repair Order."))

        return super().unlink()

    @api.onchange("lot_id")
    def onchange_lot_id(self):
        if self.lot_id:
            ro = self.env["repair.order"].search(
                [
                    ("product_id", "=", self.product_id.id),
                    ("lot_id", "=", self.lot_id.id),
                    ("state", "in", ("draft", "confirmed", "under_repair")),
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
