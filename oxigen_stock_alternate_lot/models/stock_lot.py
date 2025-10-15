# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

NOS_SIZE = 6
DN_MAX_SIZE = 15


class ProductionLot(models.Model):
    _inherit = "stock.lot"

    nos = fields.Char(
        string="NOS",
        tracking=True,
        copy=False,
        size=NOS_SIZE,
    )

    dn = fields.Char(
        string="D/N",
        tracking=True,
        copy=False,
        size=DN_MAX_SIZE,
    )

    nos_enabled = fields.Boolean(
        string="NOS Enabled", related="product_id.nos_enabled", readonly=True
    )
    dn_enabled = fields.Boolean(
        string="D/N Enabled", related="product_id.dn_enabled", readonly=True
    )

    nos_unknown = fields.Boolean(string="NOS Unknown", tracking=True)
    dn_unknown = fields.Boolean(string="D/N Unknown", tracking=True)

    unknown_readonly = fields.Boolean(compute="_compute_unknown_readonly")

    @api.depends("nos_unknown", "dn_unknown")
    def _compute_unknown_readonly(self):
        for rec in self:
            rec.unknown_readonly = not self.env.user.has_group(
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
                if rec.nos or rec.nos_unknown:
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
                if rec.dn or rec.dn_unknown:
                    raise ValidationError(
                        _("D/N is not allowed for this product %s")
                        % self.product_id.display_name
                    )

    @api.constrains("nos", "nos_unknown", "dn", "dn_unknown")
    def _check_unique_alternate_lot(self):
        for rec in self:
            if rec.nos and not rec.nos_unknown:
                domain = [
                    ("id", "!=", rec.id),
                    ("nos", "=", rec.nos),
                ]
                if rec.dn and not rec.dn_unknown:
                    domain += [
                        ("dn", "=", rec.dn),
                        ("nos_unknown", "=", False),
                        ("dn_unknown", "=", False),
                    ]
                else:
                    domain += [
                        # to avoid problems with null values
                        ("nos_unknown", "!=", True),
                    ]
                other = self.env[self._name].search(domain)
                if other:
                    raise ValidationError(
                        _(
                            "This NOS or D/N already exists "
                            "on another lot %(lot_name)s "
                            "for this product %(product_name)s"
                        )
                        % {
                            "lot_name": other.mapped("name"),
                            "product_name": self.product_id.display_name,
                        }
                    )

    @api.constrains("nos", "nos_unknown")
    def _check_nos(self):
        for rec in self:
            if rec.nos and rec.nos_unknown:
                raise ValidationError(
                    _("NOS and NOS Unknown cannot be set at the same time")
                )

    @api.constrains("dn", "dn_unknown")
    def _check_dn(self):
        for rec in self:
            if rec.dn and rec.dn_unknown:
                raise ValidationError(
                    _("D/N and D/N Unknown cannot be set at the same time")
                )

    @api.depends("nos_enabled", "dn_enabled", "nos", "dn")
    def _compute_display_name(self):
        for record in self:
            name_parts = [record.name or ""]
            if record.nos_enabled:
                if record.nos_unknown:
                    name_parts.append(_("Unknown"))
                elif record.nos:
                    name_parts.append(record.nos)
            if record.dn_enabled:
                if record.dn_unknown:
                    name_parts.append(_("Unknown"))
                elif record.dn:
                    name_parts.append(record.dn)
            record.display_name = " / ".join(filter(None, name_parts))
