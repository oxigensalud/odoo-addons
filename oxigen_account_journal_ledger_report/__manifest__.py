# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Oxigen Account Journal Ledger Report",
    "summary": "This module allows the creation of detailed "
    "journal ledger reports for Oxigen.",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "category": "Accounting",
    "depends": ["account", "report_csv"],
    "external_dependencies": {"python": ["unidecode"]},
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "wizards/oxigen_account_journal_ledger_wizard_views.xml",
        "views/menuitems.xml",
        "views/reports.xml",
    ],
}
