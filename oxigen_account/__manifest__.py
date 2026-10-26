# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Invoicing",
    "summary": "Customizations for Oxigen in Invoicing",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, NuoBiT Solutions SL",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "category": "Accounting",
    "depends": ["account_lock_date_update", "contract"],
    "license": "AGPL-3",
    "data": [
        "wizards/draft_invoices.xml",
        "views/account_move_views.xml",
        "views/report_invoice.xml",
    ],
}
