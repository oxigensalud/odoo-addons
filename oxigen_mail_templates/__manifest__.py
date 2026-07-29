# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Mail Templates",
    "summary": "Customizations for Oxigen in Templates",
    "version": "18.0.1.0.0",
    "author": "NuoBiT Solutions SL, ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting",
    "depends": ["account_invoice_batches"],
    "data": ["data/invoice_batches_templates.xml"],
    "pre_init_hook": "_pre_init_hook",
    "license": "AGPL-3",
}
