# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Oxigesti-Odoo connector",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "license": "AGPL-3",
    "category": "Connector",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "depends": [
        # "product_template_variant_definition",
        "connector",
        "partner_review",
        "sale_order_service",
        "sale_line_partner_description",
        "sale_specific_order_date",
        "oxigen_stock_alternate_lot",
        "sale",
        "stock",
    ],
    "external_dependencies": {
        "python": [
            "pymssql>=2.2.5,<3.0",
        ],
    },
    "data": [
        "data/ir_cron.xml",
        "data/queue_data.xml",
        "data/queue_job_function_data.xml",
        "views/oxigesti_backend_views.xml",
        "views/res_partner_views.xml",
        "views/product_product_views.xml",
        "views/product_category_views.xml",
        "views/product_buyerinfo_views.xml",
        "views/product_pricelist_item_views.xml",
        "views/stock_lot_views.xml",
        "views/sale_order_views.xml",
        "views/connector_oxigesti_menu.xml",
        "security/connector_oxigesti.xml",
        "security/ir.model.access.csv",
    ],
}
