# Copyright 2022 NuoBiT Solutions, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Facturae Sale Stock Service",
    "summary": "Adds a service number to delivery note on facture XML file",
    "version": "14.0.1.0.0",
    "author": "NuoBiT",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting & Finance",
    "depends": ["l10n_es_facturae_sale_stock", "sale_order_service"],
    "license": "AGPL-3",
    "data": [
        "views/report_facturae.xml",
    ],
}
