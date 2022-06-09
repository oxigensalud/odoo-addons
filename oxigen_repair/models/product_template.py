from odoo import _, api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    repair_count = fields.Float(
        compute_sudo=True,
        compute="_compute_repair",
        string="Repairs",
        help="Number of Repair Orders where the product appears as a Part",
    )
    in_repair_ids = fields.Many2many(
        comodel_name="repair.order", compute="_compute_repair", store=True
    )

    @api.depends("product_variant_ids.repair_count")
    def _compute_repair(self):
        for product in self:
            product.in_repair_ids = product.mapped("product_variant_ids.in_repair_ids")
            product.repair_count = len(
                product.in_repair_ids.filtered(
                    lambda x: x.state not in ("draft", "cancel")
                )
            )

    def action_product_template_in_rma_list(self):
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
