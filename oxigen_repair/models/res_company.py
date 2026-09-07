# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    repair_reference_manual = fields.Boolean(
        string="Manual repair reference",
        help="Repair orders of this company are created with an empty "
        "reference: the user fills it in and it is never assigned from the "
        "sequence, neither when the form opens nor when the order is saved.",
    )
