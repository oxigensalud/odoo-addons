# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Oxigen Website sale",
    "summary": "Customizations for Oxigen for Website.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Website",
    "depends": ["website_sale", "connector_woocommerce"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/product_template.xml",
        "views/product_product.xml",
    ],
}
