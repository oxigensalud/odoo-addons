# Copyright 2021 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Maintenance",
    "summary": "Customizations for Oxigen in Maintenance",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, NuoBiT Solutions SL",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "category": "Maintenance",
    "depends": [
        "stock",
        "maintenance_plan",
        "hr_maintenance",
        "maintenance_equipment_contract",
        "maintenance_equipment_hierarchy",
        "maintenance_team_hierarchy",
        "base_maintenance_group",
        "maintenance_project",
    ],
    "license": "AGPL-3",
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/maintenance_equipment_operating_system.xml",
        "views/maintenance_equipment_views.xml",
        "views/maintenance_plan_views.xml",
        "views/maintenance_request_views.xml",
        "views/contract_contract.xml",
        "views/maintenance_team_views.xml",
    ],
    "demo": ["demo/data.xml"],
}
