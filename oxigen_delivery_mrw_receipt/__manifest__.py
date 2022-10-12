# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Delivery MRW receipt",
    "summary": "Customizations for Oxigen for MRW incoming shipments",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Stock",
    "depends": ["delivery_mrw"],
    "installable": True,
    "license": "AGPL-3",
    "data": ["views/stock_picking.xml", "wizards/stock_immediate_transfer_views.xml"],
}
