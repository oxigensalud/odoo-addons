# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Mail Templates",
    "summary": "Customizations for Oxigen in Templates",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting",
    "depends": ["account_invoice_batches"],
    "data": ["data/invoice_batches_templates.xml"],
    "pre_init_hook": "_pre_init_hook",
    "installable": True,
    "license": "AGPL-3",
}
