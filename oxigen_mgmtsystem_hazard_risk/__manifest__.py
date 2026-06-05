# Copyright 2026 NuoBiT Solutions, S.L. - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Oxigen Mgmtsystem Hazard Risk",
    "summary": "Show the third hazard risk factor as Detectability",
    "version": "14.0.1.0.0",
    "author": "NuoBiT",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Management System",
    "depends": [
        "mgmtsystem_hazard_risk",
    ],
    "data": [
        "data/mgmtsystem_hazard_risk_computation_data.xml",
        "views/mgmtsystem_hazard_usage_views.xml",
    ],
    "installable": True,
    "license": "AGPL-3",
    "uninstall_hook": "uninstall_hook",
}
