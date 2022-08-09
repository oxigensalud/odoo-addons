# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen stock barcodes",
    "summary": "Specific workflow in stock barcodes for Oxigen.",
    "version": "14.0.2.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Extra Tools",
    "depends": ["stock_barcodes"],
    "data": [
        "views/stock_picking_type_views.xml",
        "wizards/stock_barcodes_read_picking_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
