# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Ambugest-Odoo connector",
    "version": "18.0.1.0.1",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "depends": [
        "partner_review",
        "sale_order_service",
        "l10n_es",
        "sale_specific_order_date",
        "connector",
    ],
    "external_dependencies": {
        "python": [
            "pymssql<=2.2.5 ; python_version <= '3.10'",
            "pymssql<=2.2.8 ; python_version < '3.12'",
            "pymssql<=2.3.7 ; python_version >= '3.12'",
        ],
    },
    "data": [
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/ambugest_backend_view.xml",
        "views/partner_view.xml",
        "views/product_product_view.xml",
        "views/sale_order_view.xml",
        "views/connector_ambugest_menu.xml",
        "security/connector_ambugest.xml",
        "security/ir.model.access.csv",
    ],
}
