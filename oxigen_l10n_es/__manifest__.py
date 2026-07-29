# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Localization",
    "summary": "Customizations to PGCE for Oxigen",
    "version": "18.0.1.0.1",
    "author": "ForgeFlow, NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting/Localizations/Account Charts",
    "depends": [
        "l10n_es",
        "l10n_es_aeat_mod303",
        "l10n_es_aeat_mod322",
        "l10n_es_aeat_mod349",
        "l10n_es_aeat_mod390",
        "l10n_es_extension",
        "l10n_es_special_prorate",
        "l10n_es_aeat_sii_oca",
    ],
    "license": "AGPL-3",
    "post_init_hook": "post_init_hook",
    "data": [
        "data/l10n.es.aeat.map.tax.line.tax.csv",
        "data/l10n.es.aeat.map.tax.line.csv",
        "data/tax_code_map_mod303_2023_data.xml",
        "data/tax_code_map_mod303_202410_data.xml",
        "data/tax_code_map_mod322_2023_data.xml",
        "data/tax_code_map_mod322_202410_data.xml",
        "data/tax_code_map_mod390_data.xml",
        "data/tax_code_map_mod390_2024_data.xml",
        "data/aeat_349_map_data.xml",
        "data/aeat_sii_map_data.xml",
    ],
}
