# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Localization",
    "summary": "Customizations to PGCE for Oxigen",
    "version": "14.0.1.4.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Accounting/Localizations/Account Charts",
    "depends": [
        "l10n_es",
        # ND handover only: guarantees load order + coexistence for the
        # 14.0.1.1.0 migration. NEVER remove within the 14 series (version
        # jumpers run old migrations under the NEWEST manifest). Drop it in
        # the next major lineage (15+/18): no pending migration there.
        "l10n_es_extension",
        "l10n_es_aeat_mod303",
        "l10n_es_aeat_mod322",
        "l10n_es_aeat_mod349",
        "account_chart_update",
        "l10n_es_dua_sii",
    ],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "data/account_chart_template_data.xml",
        "data/account_tax_data.xml",
        "data/tax_code_map_mod303_202107_data.xml",
        "data/tax_code_map_mod303_2023_data.xml",
        "data/tax_code_map_mod303_202410_data.xml",
        "data/tax_code_map_mod322_2023_data.xml",
        "data/aeat_349_map_data.xml",
        "data/account_fiscal_position_template_data.xml",
        "data/aeat_sii_map_data.xml",
        "data/fiscal_position_rege.xml",
    ],
}
