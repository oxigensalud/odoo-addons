from odoo import fields, models


class PriceListUpdate(models.Model):
    _name = 'pricelist.update'
    _description = 'Pricelist update'

    name = fields.Char(string="Name",copy=False)
    company_id = fields.Many2one('res.company', string="Company", default=lambda self: self.env.user.company_id)
    price_list_tag_ids = fields.Many2many('pricelist.tags', string="Tags")
    percentage = fields.Float(string='Percentage:')
    state = fields.Selection([('draft', 'Draft'), ('processed', 'Processed')], string="State", required=True,
                             readonly=True, copy=False, default='draft')

    def update_price_list_price(self):
        pricelist_items = self.env['product.pricelist'].search([('company_id', '=', self.company_id.id), (
            'price_list_tag_ids', 'in', self.price_list_tag_ids.ids)]).mapped('item_ids').filtered(
            lambda item: item.compute_price == 'fixed')
        for items in pricelist_items:
            new_price = (items.fixed_price * (self.percentage / 100))
            items.fixed_price = (items.fixed_price + new_price)
        if pricelist_items:
            self.state = 'processed'

    _sql_constraints = [
        ('name', 'unique (name)', 'The name must be unique !')
    ]
