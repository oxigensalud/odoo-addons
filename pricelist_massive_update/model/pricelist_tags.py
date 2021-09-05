from odoo import fields, models, _, api
from odoo.exceptions import ValidationError


class PriceListTags(models.Model):
    _name = 'pricelist.tags'
    _description = 'Pricelist tags'

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    parent_id = fields.Many2one('pricelist.tags', string="Parent Id", ondelete='restrict', index=True)

    _sql_constraints = [
        ('name', 'unique (name)', 'The name must be unique !')
    ]

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise ValidationError(_('Error! You cannot add recursive categories.'))

    @api.multi
    def name_get(self):
        res = []
        for pricelist_tag in self:
            names = []
            current = pricelist_tag
            while current:
                names.append(pricelist_tag.name)
                current = pricelist_tag.parent_id
            res.append((pricelist_tag.id, ' / '.join(reversed(names))))
        return res

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        if name:
            name = name.split(' / ')[-1]
            args = [('name', operator, name)] + args
        return self.search(args, limit=limit).name_get()
