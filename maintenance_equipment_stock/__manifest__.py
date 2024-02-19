# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Maintenance Equipment Stock",
    "summary": """
        Create equipments from stocks""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "depends": [
        "maintenance",
        "purchase_stock",
        "product_brand",
    ],
    "data": [
        "views/stock_picking.xml",
        "views/stock_production_lot.xml",
        "views/maintenance_equipment.xml",
        "views/product_template.xml",
    ],
    "demo": [],
}
