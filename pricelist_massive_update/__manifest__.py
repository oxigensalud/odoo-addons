# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{

    'name': 'Price List Massive Update',
    'version': '11.0.15.03.2020',
    'category': 'Sale',
    'license': 'OPL-1',
    'author': 'Vraja Technologies',
    'website': 'http://www.vrajatechnologies.com',
    'description': """ update price according pricelist tags
    """,
    'depends': ['base', 'sale'],

    'data': [
        'security/ir.model.access.csv',
        'view/pricelist_tags.xml',
        'view/product_pricelist.xml',
        'view/pricelist_update.xml'
    ],

    'installable': True,
    'active': False,
}
