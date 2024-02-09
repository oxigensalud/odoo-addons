# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    nos_enabled = fields.Boolean(string="NOS", tracking=True)
    dn_enabled = fields.Boolean(string="D/N", tracking=True)

    @api.constrains("nos_enabled", "dn_enabled", "tracking")
    def _check_alternate_lot(self):
        for rec in self:
            if rec.tracking == "serial":
                if rec.dn_enabled and not rec.nos_enabled:
                    raise ValidationError(_("NOS must be selected if D/N is selected"))
            else:
                if rec.nos_enabled or rec.dn_enabled:
                    raise ValidationError(
                        _(
                            "NOS and D/N are not allowed for products without serial number"
                        )
                    )

    def write(self, vals):
        if "nos_enabled" in vals:
            if self.nos_enabled and not vals["nos_enabled"]:
                lots = self.env["stock.production.lot"].search(
                    [
                        ("product_id.product_tmpl_id", "=", self.id),
                        ("nos", "!=", False),
                    ]
                )
                if lots:
                    raise ValidationError(
                        _("You cannot disable NOS, it still exists lots with NOS")
                    )
        if "dn_enabled" in vals:
            if self.dn_enabled and not vals["dn_enabled"]:
                lots = self.env["stock.production.lot"].search(
                    [
                        ("product_id.product_tmpl_id", "=", self.id),
                        ("dn", "!=", False),
                    ]
                )
                if lots:
                    raise ValidationError(
                        _("You cannot disable D/N, it still exists lots with D/N")
                    )
        return super(ProductTemplate, self).write(vals)
