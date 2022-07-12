# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Transport Document Report",
    "summary": "Transport Document Report for Oxigen",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Warehouse",
    "depends": ["stock", "fleet", "hr"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "views/transport_company_views.xml",
        "views/transport_shipper_views.xml",
        "views/product_container_views.xml",
        "views/product_views.xml",
        "views/stock_picking_views.xml",
        "views/stock_move_views.xml",
        "views/fleet_vehicle_views.xml",
        "report/report_transport_document.xml",
        "report/stock_report_views.xml",
    ],
}
