# Copyright 2023 Dixmit
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Oxigen Maintenance Gitlab",
    "summary": """
        Integrate maintenance with gitlab""",
    "version": "18.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit, NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "depends": [
        "maintenance_project",
    ],
    "external_dependencies": {
        "python": ["python-gitlab", "responses"],
    },
    "data": [
        "views/maintenance_request.xml",
        "views/project_project.xml",
    ],
}
