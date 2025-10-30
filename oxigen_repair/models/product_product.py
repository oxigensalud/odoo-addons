from collections import defaultdict

from odoo import _, api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    repair_count = fields.Float(
        compute_sudo=True,
        compute="_compute_repair_count",
        string="Repairs",
        help="Number of Repair Orders where the product appears as a Part",
    )
    in_repair_ids = fields.Many2many(
        comodel_name="repair.order", compute="_compute_repair", store=True
    )

    def _compute_repair(self):
        product_rma_dict = defaultdict(list)

        for move in self.env["stock.move"].search(
            [
                ("company_id", "in", self.env.company.ids),
                ("product_id", "in", self.ids),
            ]
        ):
            if move.repair_id:
                product_rma_dict[move.product_id.id].append(move.repair_id.id)
        for product in self:
            product.in_repair_ids = product_rma_dict.get(product.id, [])

    @api.depends("in_repair_ids.state")
    def _compute_repair_count(self):
        self.repair_count = len(
            self.in_repair_ids.filtered(lambda x: x.state not in ("draft", "cancel"))
        )

    def action_product_product_in_rma_list(self):
        domain = [
            ("id", "in", self.in_repair_ids.ids),
        ]
        context = {
            "search_default_not_draft": 1,
        }

        action = {
            "name": _("Repair Orders"),
            "type": "ir.actions.act_window",
            "res_model": "repair.order",
            "view_type": "list",
            "view_mode": "list,form",
            "domain": domain,
            "context": context,
        }
        return action
