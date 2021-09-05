from odoo import fields, models


class ProductPriceList(models.Model):
    _inherit = 'product.pricelist'

    price_list_tag_ids = fields.Many2many('pricelist.tags', string="Tags")
