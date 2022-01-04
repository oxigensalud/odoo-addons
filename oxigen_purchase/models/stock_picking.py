# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class Picking(models.Model):
    _inherit = "stock.picking"
    # Rename standard `Reference` label to not have duplicated labels
    name = fields.Char(string="Name")

    def write(self, vals):
        if "partner_ref" in vals:
            for rec in self.filtered(lambda r: r.purchase_id):
                if not rec.purchase_id.partner_ref:
                    rec.purchase_id.partner_ref = vals["partner_ref"]

                else:
                    l_pref = rec.purchase_id.partner_ref.split(", ")
                    refs = [
                        x.partner_ref
                        for x in rec.purchase_id.picking_ids
                        if x.id != rec.id
                    ]
                    if rec.partner_ref in l_pref and rec.partner_ref not in refs:
                        l_pref.remove(rec.partner_ref)

                    if vals["partner_ref"] not in l_pref:
                        l_pref.append(vals["partner_ref"])

                    rec.purchase_id.partner_ref = ", ".join(l_pref)

        return super(Picking, self).write(vals)
