from collections import defaultdict

from odoo import _, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    repair_count = fields.Float(
        compute_sudo=True,
        compute="_compute_repair",
        string="Repairs",
        help="Number of Repair Orders where the product appears as a Part",
    )
    in_repair_ids = fields.Many2many(
        comodel_name="repair.order", compute="_compute_repair", store=True
    )

    def _compute_repair(self):
        self.repair_count = 0
        product_rma_dict = defaultdict(list)
        [
            product_rma_dict[operation.product_id.id].append(operation.repair_id.id)
            for operation in self.env["repair.line"].search(
                [
                    ("company_id", "in", self.env.company.ids),
                    ("product_id", "in", self.ids),
                ]
            )
        ]
        for product in self:
            if not product.id:
                product.repair_count = 0.0
                continue
            product.in_repair_ids = product_rma_dict.get(product.id, [])
            product.repair_count = len(
                product.in_repair_ids.filtered(
                    lambda x: x.state not in ("draft", "cancel")
                )
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
