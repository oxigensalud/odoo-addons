# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Localization",
    "summary": "Customizations to PGCE for Oxigen",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting/Localizations/Account Charts",
    "depends": [
        "l10n_es",
        "l10n_es_aeat_mod303",
        "l10n_es_special_prorate",
        "account_chart_update",
        "l10n_es_dua_sii",
    ],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "data/account_chart_template_data.xml",
        "data/account_tax_data.xml",
        "data/legacy_account_tax_data.xml",
        "data/tax_code_map_mod303_data.xml",
        "data/account_fiscal_position_template_data.xml",
        "data/oxigen_fiscal_position_extracomunitaria.xml",
        "data/aeat_sii_map_data.xml",
    ],
}
