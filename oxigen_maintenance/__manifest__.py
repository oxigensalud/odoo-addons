# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Maintenance",
    "summary": "Customizations for Oxigen in Maintenance",
    "version": "11.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Maintenance",
    "depends": ["stock", "maintenance_plan"],
    "installable": True,
    "license": "AGPL-3",
    "data": ["views/stock_location_views.xml", "views/maintenance_views.xml"],
}
