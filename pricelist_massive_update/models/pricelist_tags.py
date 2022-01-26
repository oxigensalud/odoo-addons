# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class PriceListTags(models.Model):
    _name = "pricelist.tags"
    _description = "Pricelist tags"

    name = fields.Char(string="Name")
    active = fields.Boolean(string="Active", default=True)
    parent_id = fields.Many2one(
        comodel_name="pricelist.tags",
        string="Parent Id",
        ondelete="restrict",
    )

    _sql_constraints = [("name", "unique (name)", "The name must be unique !")]

    @api.constrains("parent_id")
    def _check_hierarchy(self):
        for record in self:
            if not record._check_recursion():
                raise ValidationError(_("Error! You cannot add recursive categories."))

    def name_get(self):
        res = []
        for record in self:
            names = []
            current = record
            while current:
                names.append(record.name)
                current = current.parent_id
            res.append((record.id, " / ".join(reversed(names))))
        return res

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        args = args or []
        if name:
            name = name.split(" / ")[-1]
            args = [("name", operator, name)] + args
        return self.search(args, limit=limit).name_get()
