# Copyright Dixmit
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Special prorate tax mapping for 322",
    "summary": "This module adds the 322 model special prorate taxes",
    "version": "14.0.1.0.0",
    "category": "Sales",
    "author": "Dixmit",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_special_prorate",
        "l10n_es_aeat_mod322",
    ],
    "data": [
        "data/tax_code_map_mod322_2023_data.xml",
    ],
    "installable": True,
    "auto_install": True,
}
