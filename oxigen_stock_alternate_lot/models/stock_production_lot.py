# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

NOS_SIZE = 6
DN_MAX_SIZE = 15


class ProductionLot(models.Model):
    _inherit = "stock.production.lot"

    nos = fields.Char(
        string="NOS",
        tracking=True,
        copy=False,
        compute="_compute_nos",
        store=True,
        readonly=False,
        size=NOS_SIZE,
    )

    @api.depends("nos_unknown")
    def _compute_nos(self):
        for rec in self:
            if rec.nos_unknown:
                rec.nos = None

    dn = fields.Char(
        string="D/N",
        tracking=True,
        copy=False,
        compute="_compute_dn",
        store=True,
        readonly=False,
        size=DN_MAX_SIZE,
    )

    @api.depends("dn_unknown")
    def _compute_dn(self):
        for rec in self:
            if rec.dn_unknown:
                rec.dn = None

    nos_enabled = fields.Boolean(
        string="NOS Enabled", related="product_id.nos_enabled", readonly=True
    )
    dn_enabled = fields.Boolean(
        string="D/N Enabled", related="product_id.dn_enabled", readonly=True
    )

    nos_unknown = fields.Boolean(
        string="NOS Unknown", tracking=True, required=True, default=True
    )
    dn_unknown = fields.Boolean(
        string="D/N Unknown", tracking=True, required=True, default=True
    )

    unknown_readonly = fields.Boolean(compute="_compute_unknown_readonly")

    @api.depends("nos_unknown", "dn_unknown")
    def _compute_unknown_readonly(self):
        for rec in self:
            rec.unknown_readonly = not rec.user_has_groups(
                "oxigen_stock_alternate_lot.group_update_lot_unknown_field"
            )

    @api.constrains("nos")
    def _check_nos_size(self):
        for rec in self:
            if rec.nos and len(rec.nos) != NOS_SIZE:
                raise ValidationError(
                    _("NOS must be exactly %i characters long") % NOS_SIZE
                )

    @api.constrains("dn")
    def _check_dn_size(self):
        for rec in self:
            if rec.dn and len(rec.dn) > DN_MAX_SIZE:
                raise ValidationError(
                    _("D/N must be less or equal than %i characters long") % DN_MAX_SIZE
                )

    @api.constrains("nos", "nos_unknown", "dn", "dn_unknown")
    def _check_alternate_lot(self):
        for rec in self:
            if rec.nos_enabled:
                if not rec.nos and not rec.nos_unknown:
                    raise ValidationError(
                        _("NOS must be defined in this product %s")
                        % self.product_id.display_name
                    )
            else:
                if rec.nos:
                    raise ValidationError(
                        _("NOS is not allowed in this product %s")
                        % self.product_id.display_name
                    )
            if rec.dn_enabled:
                if not rec.dn and not rec.dn_unknown:
                    raise ValidationError(
                        _("D/N must be defined in this product %s")
                        % self.product_id.display_name
                    )
            else:
                if rec.dn:
                    raise ValidationError(
                        _("D/N is not allowed for this product %s")
                        % self.product_id.display_name
                    )

    @api.constrains("nos", "nos_unknown", "dn", "dn_unknown")
    def _check_unique_alternate_lot(self):
        for rec in self:
            if rec.nos and not rec.nos_unknown:
                if rec.dn and not rec.dn_unknown:
                    domain = [
                        ("id", "!=", rec.id),
                        "&",
                        ("nos", "=", rec.nos),
                        ("dn", "=", rec.dn),
                        ("nos_unknown", "=", False),
                        ("dn_unknown", "=", False),
                    ]
                else:
                    domain = [
                        ("id", "!=", rec.id),
                        ("nos", "=", rec.nos),
                        ("nos_unknown", "!=", True),
                    ]
                other = self.env[self._name].search(domain)
                if other:
                    raise ValidationError(
                        _(
                            "This NOS or D/N already exists on another lot %s "
                            "for this product %s"
                        )
                        % (other.mapped("name"), self.product_id.display_name)
                    )

    @api.depends("nos_enabled", "dn_enabled", "nos", "dn")
    def name_get(self):
        res = []
        for record in self:
            name_l = [record.name]
            if record.nos_enabled:
                name_l.append((record.nos_unknown and _("Unknown")) or record.nos or "")
            if record.dn_enabled:
                name_l.append((record.dn_unknown and _("Unknown")) or record.dn or "")
            name = " / ".join(name_l)
            res.append((record.id, name))
        return res
