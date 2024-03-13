# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen stock barcodes GS1",
    "summary": "Specific GS1 barcode scanning logic for Oxigen.",
    "version": "14.0.2.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Extra Tools",
    "depends": [
        "stock_barcodes_gs1_expiry",
        "oxigen_stock_barcodes",
        "product_multi_barcode",
    ],
    "data": ["wizard/stock_barcodes_new_lot_views.xml"],
    "installable": True,
    "license": "AGPL-3",
}
