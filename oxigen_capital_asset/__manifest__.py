# Copyright NuoBiT - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Oxigen Capital Asset",
    "summary": "This module adds a custom view to show all the capital asset "
    "fields in a tab in asset",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_account_capital_asset",
        "l10n_es_aeat_prorate_asset",
    ],
    "data": [
        "views/account_asset.xml",
    ],
}
