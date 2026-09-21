# Copyright 2022 ForgeFlow S.L.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Invoicing",
    "summary": "Customizations for Oxigen in Invoicing",
    "version": "14.0.1.0.2",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting",
    "depends": ["account_lock_date_update", "contract", "hr_expense"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "wizards/draft_invoices.xml",
        "views/account_move_views.xml",
        "views/report_invoice.xml",
    ],
}
