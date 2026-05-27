# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Oxigen Document Page",
    "summary": "Oxigen customizations on document pages: 10-digit reference "
    "auto-generation and archive wizard with mandatory reason.",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Knowledge Management",
    "depends": [
        "document_page_reference",
    ],
    "data": [
        "security/ir.model.access.csv",
        "wizards/document_page_archive_wizard.xml",
    ],
}
