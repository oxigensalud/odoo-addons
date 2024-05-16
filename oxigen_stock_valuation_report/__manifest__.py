# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Oxigen Stock Valuation Report",
    "summary": "This module allows the creation of detailed inventory "
    "valuation reports for Oxigen.",
    "version": "14.0.1.0.0",
    "author": "Nuobit Solutions, S.L.",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting",
    "depends": ["account", "report_xlsx"],
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/reports.xml",
        "wizards/oxigen_stock_valuation_wizard_views.xml",
        "views/menuitems.xml",
    ],
}
