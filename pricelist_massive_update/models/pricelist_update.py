# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo import fields, models


class PriceListUpdate(models.Model):
    _name = "pricelist.update"
    _description = "Pricelist update"

    name = fields.Char(string="Name", copy=False)
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        default=lambda self: self.env.company,
    )
    price_list_tag_ids = fields.Many2many(comodel_name="pricelist.tags", string="Tags")
    percentage = fields.Float(string="Percentage:")
    state = fields.Selection(
        selection=[("draft", "Draft"), ("processed", "Processed")],
        string="State",
        required=True,
        readonly=True,
        copy=False,
        default="draft",
    )

    def update_price_list_price(self):
        for record in self:
            pricelist_items = self.env["product.pricelist.item"].search(
                [
                    ("pricelist_id.company_id", "in", (record.company_id.id, False)),
                    (
                        "pricelist_id.price_list_tag_ids",
                        "in",
                        record.price_list_tag_ids.ids,
                    ),
                    ("compute_price", "=", "fixed"),
                ]
            )
            for items in pricelist_items:
                new_price = items.fixed_price * (record.percentage / 100)
                items.fixed_price = items.fixed_price + new_price
            if pricelist_items:
                record.state = "processed"

    _sql_constraints = [("name", "unique (name)", "The name must be unique !")]
