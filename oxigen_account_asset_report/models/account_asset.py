# Copyright NuoBiT - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import FORMATS


def insert_after(lst, item, new_items):
    if not isinstance(new_items, (list, tuple)):
        new_items = (new_items,)
    for i, e in enumerate(lst):
        if e == item:
            for j, ni in enumerate(new_items, 1):
                lst.insert(i + j, ni)
            break


class AccountAsset(models.Model):
    _inherit = "account.asset"

    @api.model
    def _xls_acquisition_fields(self):
        fields = super()._xls_acquisition_fields()
        insert_after(fields, "date_start", ["date_remove", "date_transfer"])
        return fields

    @api.model
    def _xls_active_fields(self):
        fields = super()._xls_active_fields()
        insert_after(fields, "date_start", ["date_remove", "date_transfer"])
        return fields

    @api.model
    def _xls_removal_fields(self):
        fields = super()._xls_removal_fields()
        insert_after(fields, "date_remove", "date_transfer")
        return fields

    @api.model
    def _xls_asset_template(self):
        asset_template = super()._xls_asset_template()
        AssetReport = self.env["report.account_asset_management.asset_report_xls"]
        return {
            "date_transfer": {
                "header": {
                    "type": "string",
                    "value": AssetReport._("Asset Transfer Date"),
                },
                "asset": {
                    "value": AssetReport._render("asset.date_transfer or ''"),
                    "format": FORMATS["format_tcell_date_left"],
                },
                "width": 20,
            },
            **asset_template,
        }
