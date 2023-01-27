# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Price List Massive Update",
    "summary": "Update pricelists according to pricelist tags",
    "version": "14.0.1.0.1",
    "category": "Sale",
    "license": "AGPL-3",
    "author": "Vraja Technologies",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "depends": ["base", "sale"],
    "data": [
        "security/ir.model.access.csv",
        "views/pricelist_tags.xml",
        "views/product_pricelist.xml",
        "views/pricelist_update.xml",
    ],
    "installable": True,
}
