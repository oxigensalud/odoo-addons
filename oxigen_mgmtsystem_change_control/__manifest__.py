# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Oxigen Management System Change Control",
    "summary": "Adapt the management system Reviews entity to act as the "
    "Oxigen change control record",
    "version": "14.0.1.0.0",
    "category": "Management System",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "mgmtsystem_review",
        "mgmtsystem_review_copy_lines",
    ],
    "data": [
        "views/mgmtsystem_review_views.xml",
    ],
    "uninstall_hook": "uninstall_hook",
}
