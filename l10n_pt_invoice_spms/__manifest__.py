# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "L10n Pt Invoice Spms",
    "summary": """Send invoices to SPMS""",
    "version": "14.0.1.0.0",
    "license": "AGPL-3",
    "author": "Dixmit,Odoo Community Association (OCA)",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "depends": [
        "ptplus_edi",
        "edi_account_oca",
    ],
    "external_dependencies": {"python": ["zeep", "xmlsig"]},
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/spms_system.xml",
        "views/spms_lot.xml",
        "views/spms_prescription_type.xml",
        "views/spms_context.xml",
        "views/spms_suspension_reason.xml",
        "views/account_move.xml",
        "views/account_move_line.xml",
        "views/res_company.xml",
        "views/res_partner.xml",
        "data/edi.xml",
        "data/spms_templates.xml",
    ],
    "demo": [],
}
