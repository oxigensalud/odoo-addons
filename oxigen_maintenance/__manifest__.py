# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Maintenance",
    "summary": "Customizations for Oxigen in Maintenance",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Maintenance",
    "depends": [
        "stock",
        "maintenance_plan",
        "hr_maintenance",
        "maintenance_equipment_contract",
    ],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/stock_location_views.xml",
        "views/maintenance_equipment_views.xml",
        "views/maintenance_plan_views.xml",
        "views/maintenance_request_views.xml",
        "views/contract_contract.xml",
    ],
}
