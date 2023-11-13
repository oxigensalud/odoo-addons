# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo import _, fields, models
from odoo.exceptions import ValidationError


class AssetProrateRegularization(models.Model):
    _inherit = "capital.asset.prorate.regularization"

    mod322_id = fields.Many2one(
        comodel_name="l10n.es.aeat.mod322.report",
        string="Model 322",
        readonly=True,
        ondelete="restrict",
        index=True,
    )

    def _get_by_year_322(self, mod322):
        asset_regularization_line = self.filtered(lambda x: x.year == mod322.year)
        if asset_regularization_line:
            if not asset_regularization_line.mod322_id:
                raise ValidationError(
                    _(
                        "This asset have a prorate regularization"
                        " line this year: %s, but it's not related"
                        " with a model 322. Please, review prorate"
                        " regularizations of capital asset: %s"
                    )
                    % (mod322.year, self.mapped("asset_id.name"))
                )
            elif asset_regularization_line.mod303_id != mod322:
                raise ValidationError(
                    _(
                        "This asset have a prorate regularization"
                        " line this year: %s,"
                        " but related with another model 303. "
                        "Please, review prorate regularizations "
                        "of capital asset: %s"
                    )
                    % (mod322.year, self.mapped("asset_id.name"))
                )
        return asset_regularization_line

    def unlink(self):
        allow_delete_capital_asset_lines = self.env.context.get(
            "allow_delete_capital_asset_lines", False
        )
        for rec in self:
            if rec.mod322_id and not allow_delete_capital_asset_lines:
                raise ValidationError(
                    _(
                        "You can't delete a capital asset regularization line "
                        "if it's linked with a model 322."
                    )
                )
        return super().unlink()
