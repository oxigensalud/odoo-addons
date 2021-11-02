# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen stock barcodes",
    "summary": "It allows to see picking information when scanning barcodes",
    "version": "11.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Extra Tools",
    "depends": ["stock_barcodes"],
    "data": [
        "views/barcodes_assets_backend.xml",
        "wizard/stock_barcodes_read_picking_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
}
