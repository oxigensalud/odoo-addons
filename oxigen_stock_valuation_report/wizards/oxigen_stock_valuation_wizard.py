# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
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

    def _print_report(self):
        self.ensure_one()
        report = self.env.ref(
            "oxigen_stock_valuation_report.report_oxigen_stock_valuation_xlsx_action"
        )
        return report.report_action(
            self,
            data={
                "company_id": self.company_id.id,
                "date": self.date,
                "tz": self.env.context["tz"],
            },
        )

    def button_export_xlsx(self):
        self.ensure_one()
        return self._print_report()
