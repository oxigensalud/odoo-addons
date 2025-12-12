# Copyright 2022 NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Facturae Sale Stock Service",
    "summary": "Adds a service number to delivery note on facture XML file",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "category": "Accounting & Finance",
    "depends": ["l10n_es_facturae_sale_stock", "sale_order_service"],
    "license": "AGPL-3",
    "data": [
        "views/report_facturae.xml",
    ],
}
