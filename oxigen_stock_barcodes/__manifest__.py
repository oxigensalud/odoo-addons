# Copyright 2021 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen stock barcodes",
    "summary": "Specific workflow in stock barcodes for Oxigen.",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Extra Tools",
    "depends": ["stock_barcodes", "oxigen_stock_alternate_lot"],
    "data": [
        "views/stock_picking_type_views.xml",
        "wizards/stock_barcodes_read_picking_views.xml",
    ],
    "license": "AGPL-3",
}
