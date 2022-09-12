# Copyright 2022 NuoBiT Solutions, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Stock Alternate Lot",
    "summary": "Alternative serial numbers",
    "version": "14.0.1.0.1",
    "author": "NuoBiT",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Warehouse",
    "depends": ["stock"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "security/res_groups.xml",
        "views/product_template.xml",
        "views/stock_production_lot_views.xml",
    ],
}
