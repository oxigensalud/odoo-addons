# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import fields, models


class OxigenStockValuationWizard(models.TransientModel):
    _name = "oxigen.stock.valuation.wizard"
    _description = "Oxigen Stock Valuation Wizard"

    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        readonly=True,
    )
    date = fields.Date(required=True)

    def _print_report(self, report_type):
        self.ensure_one()
        report_name = "report_oxigen_stock_valuation_xlsx"
        return (
            self.env["ir.actions.report"]
            .search(
                [("report_name", "=", report_name), ("report_type", "=", report_type)],
                limit=1,
            )
            .report_action(
                self,
                data={
                    "company_id": self.company_id.id,
                    "date": self.date,
                    "tz": self.env.context["tz"],
                },
            )
        )

    def button_export_xlsx(self):
        self.ensure_one()
        report_type = "xlsx"
        return self._print_report(report_type)
