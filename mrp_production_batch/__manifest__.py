# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "MRP Production Batch",
    "summary": "Customizations for Oxigen in MRP Production",
    "version": "14.0.1.0.0",
    "author": "NuoBiT Solutions SL",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Manufacturing/Manufacturing",
    "depends": ["mrp"],
    "installable": True,
    "license": "AGPL-3",
    "data": [
        "security/ir.model.access.csv",
        "data/ir_sequence_data.xml",
        "views/mrp_production_batch_views.xml",
        "views/mrp_production_views.xml",
        "views/stock_picking_views.xml",
        "wizard/wizard_mrp_production_batch.xml",
    ],
}
