# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "AEAT 303 - Special Prorate Regularization Capital Asset",
    "summary": "This module allows to regularize capital assets "
    "prorate differences on 322 report",
    "version": "14.0.1.0.0",
    "category": "Accounting",
    "author": "Dixmit",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "license": "AGPL-3",
    "depends": [
        "l10n_es_aeat_mod322_special_prorate_regularization",
        "l10n_es_aeat_mod303_special_prorate_regularization_capital_asset",
    ],
    "data": [
        "views/mod322_views.xml",
        "views/account_asset.xml",
    ],
}
