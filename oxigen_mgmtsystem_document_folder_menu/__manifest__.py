# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Oxigen Management System Document Folder Menu",
    "summary": "Browse the management system document menus by folder",
    "version": "18.0.1.0.0",
    "category": "Management System",
    "author": "Oxigen Salud SA, NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "document_page_environmental_aspect",
        "document_page_procedure",
        "document_page_work_instruction",
        "mgmtsystem_manual",
    ],
    "data": [
        "views/document_page_views.xml",
    ],
    "auto_install": True,
    "uninstall_hook": "uninstall_hook",
}
