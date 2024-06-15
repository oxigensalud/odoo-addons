# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Oxigen Product",
    "summary": "Customizations for Oxigen in Product application",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions, S.L.",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Product",
    # TODO: review dependencies.
    "depends": ["product","website_sale"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/product_template.xml",
    ],
}
