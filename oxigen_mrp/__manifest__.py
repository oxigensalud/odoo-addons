# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "Oxigen MRP",
    "summary": "Customizations for Oxigen in MRP application",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Manufacturing/Manufacturing",
    "depends": ["mrp"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "views/product_template.xml",
        "views/stock_production_lot_views.xml",
    ],
}
