# Copyright 2021 ForgeFlow S.L.
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Oxigen Repair",
    "summary": "Custumizations for Oxigen in Repairs application",
    "version": "14.0.1.1.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Inventory/Inventory",
    "depends": ["repair"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/repair_views.xml",
        "views/product_product.xml",
        "views/product_template.xml",
        "views/res_config_settings_views.xml",
    ],
}
