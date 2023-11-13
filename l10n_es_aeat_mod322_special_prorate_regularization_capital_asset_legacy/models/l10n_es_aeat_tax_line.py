# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class L10nEsAeatTaxLine(models.Model):
    _inherit = "l10n.es.aeat.tax.line"

    asset_ids = fields.Many2many(
        string="Assets",
        comodel_name="account.asset",
    )
    mod322_id = fields.Many2one(
        string="Model 322",
        comodel_name="l10n.es.aeat.mod322.report",
        compute="_compute_mod322_id",
    )
    mod322_period_type = fields.Selection(related="mod322_id.period_type")

    def _compute_mod322_id(self):
        for rec in self:
            if rec.model == "l10n.es.aeat.mod322.report":
                rec.mod322_id = self.env[rec.model].browse(rec.res_id)
            else:
                rec.mod322_id = False

    def get_calculated_assets(self):
        action_dict = (
            self.env.ref("account_asset_management.account_asset_action")
            .sudo()
            .read()[0]
        )
        action_dict["domain"] = [("id", "in", self.asset_ids.ids)]
        return action_dict
