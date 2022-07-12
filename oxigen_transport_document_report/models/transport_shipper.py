# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, fields, models


class TransportShipper(models.Model):
    _name = "transport.shipper"
    _description = "Transport Shipper"

    name = fields.Char(string="Name", required=True)
    full_name = fields.Char(
        string="Full Name", related="name", required=True, store=True, readonly=False
    )
    identification_id = fields.Char(
        string="Identification No",
        related="user_id.employee_id.identification_id",
        store=True,
        readonly=False,
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_partner_id",
        inverse="_inverse_partner_id",
        store=True,
        readonly=False,
        string="Corresponding contact",
        domain="[('parent_id','!=', False), ('is_company','=', False)]",
    )
    user_ids = fields.One2many(comodel_name="res.users", related="partner_id.user_ids")
    user_id = fields.Many2one(
        comodel_name="res.users",
        domain="[('partner_id', '=', partner_id)]",
    )
    image_1920 = fields.Image(related="partner_id.image_1920")
    transport_company_id = fields.Many2one(
        comodel_name="transport.company",
        string="Transport Company",
    )
    company_id = fields.Many2one(
        related="transport_company_id.company_id", default=lambda self: self.env.company
    )
    has_partner = fields.Boolean(
        string="Has partner", compute="_compute_has_partner", store=True
    )

    @api.depends("partner_id")
    def _compute_has_partner(self):
        for shipper in self:
            shipper.has_partner = bool(shipper.partner_id)

    @api.depends("name", "company_id")
    def _compute_partner_id(self):
        for shipper in self:
            if not self.name:
                shipper.partner_id = False
                continue
            partner = self.env["res.partner"].search(
                [
                    ("name", "ilike", shipper.name),
                    ("parent_id", "!=", False),
                    ("is_company", "=", False),
                    "|",
                    ("company_id", "=", shipper.company_id.id),
                    ("company_id", "=", False),
                ],
                limit=1,
            )
            if partner:
                shipper.partner_id = partner
            else:
                shipper.partner_id = False

    def _inverse_partner_id(self):
        for shipper in self:
            if shipper.name != shipper.partner_id.name:
                shipper.name = shipper.partner_id.name

    @api.onchange("partner_id")
    def _compute_name(self):
        self._inverse_partner_id()
