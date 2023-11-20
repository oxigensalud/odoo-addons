# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Oxigen Maintenance Gitlab",
    "summary": """
        Integrate maintenance with gitlab""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "depends": [
        "maintenance_project",
    ],
    "external_dependencies": {
        "python": ["gitlab"],
    },
    "data": [
        "views/maintenance_request.xml",
        "views/project_project.xml",
    ],
    "demo": [],
}
