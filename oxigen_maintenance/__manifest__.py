# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Maintenance",
    "summary": "Customizations for Oxigen in Maintenance",
    "version": "14.0.1.3.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Maintenance",
    "depends": [
        "stock",
        "maintenance_plan",
        "hr_maintenance",
        "maintenance_equipment_contract",
        "maintenance_equipment_hierarchy",
        "maintenance_team_hierarchy",
        "base_maintenance_group",
    ],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/maintenance_equipment_operating_system.xml",
        "views/stock_location_views.xml",
        "views/maintenance_equipment_views.xml",
        "views/maintenance_plan_views.xml",
        "views/maintenance_request_views.xml",
        "views/contract_contract.xml",
        "views/maintenance_team_views.xml",
    ],
    "demo": ["demo/data.xml"],
}
