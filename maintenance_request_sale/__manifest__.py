# Copyright 2023 Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Maintenance Request Sale",
    "summary": """
        This is a bridge module between Maintenance and Sale""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "category": "Maintenance",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "depends": [
        "maintenance",
        "sale",
    ],
    "data": [
        "views/maintenance_request.xml",
        "views/sale_order.xml",
    ],
}
