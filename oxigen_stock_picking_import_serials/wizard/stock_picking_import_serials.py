# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import datetime


class StockPickingImportSerials(models.TransientModel):
    _inherit = "stock.picking.import.serials"

    def _prepare_additional_tracking_values(self, data, company):
        res = super()._prepare_additional_tracking_values(data, company)
        data_dict = {
            **res,
            **dict(
                zip(
                    [
                        "nos",
                        "dn",
                        "manufacturer",
                        "weight",
                        "manufacture_date",
                        "retesting_date",
                        "next_retesting_date",
                        "valid_until_date",
                    ],
                    data,
                )
            ),
        }
        if data_dict["manufacturer"]:
            sp_company_id = (
                self.env["stock.picking"]
                .browse(self.env.context["active_id"])
                .company_id.id
            )
            manufacturer = self.env["res.partner"].search(
                [
                    ("name", "=", data_dict["manufacturer"]),
                    ("company_id", "in", [sp_company_id, False]),
                ]
            )
            if len(manufacturer) > 1:
                raise UserError(
                    _("There are more than one manufacturer with the same name %s")
                    % data_dict["manufacturer"]
                )
            if not manufacturer:
                raise UserError(
                    _("The manufacturer %s doesn't exist") % data_dict["manufacturer"]
                )
            data_dict["manufacturer"] = manufacturer.id
        fields_to_check = [
            "manufacture_date",
            "retesting_date",
            "next_retesting_date",
            "valid_until_date",
        ]
        for field in fields_to_check:
            field_type = self.env["stock.production.lot"].fields_get()[field]["type"]
            if (
                data_dict[field]
                and field_type == "date"
                and not isinstance(data_dict[field], datetime.datetime)
            ):
                raise UserError(
                    _(
                        "The value of %s format %s is not valid."
                        " Please enter a valid date format"
                    )
                    % (field, data_dict[field])
                )
        return data_dict
