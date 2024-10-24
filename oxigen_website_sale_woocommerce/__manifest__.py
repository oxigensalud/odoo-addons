# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

{
    "name": "Oxigen Website sale Woocommerce",
    "summary": "Customizations for Oxigen for Website.",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Website",
    "depends": ["oxigen_website_sale_extra_fields", "connector_woocommerce"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/product_template.xml",
        "views/product_product.xml",
    ],
}
