# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSupplierInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass()

        # ENVIRONMENTS
        cls.account_account = cls.env["account.account"]
        cls.account_move = cls.env["account.move"].with_context(tracking_disable=True)

        # INSTANCES
        cls.partner = cls.env.ref("base.res_partner_2")
        # Account for invoice
        cls.account = cls.account_account.search(
            [
                (
                    "account_type",
                    "=",
                    "asset_receivable",
                )
            ],
            limit=1,
        )

    def test_check_unique_supplier_invoice_number_insensitive(self):
        # Invoice with unique reference 'ABC123'
        move1 = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "invoice_date": fields.Date.today(),
                "move_type": "in_invoice",
                "ref": "ABC123",
                "invoice_line_ids": [(0, 0, {"partner_id": self.partner.id})],
            }
        )
        move1.action_post()

        # A new invoice instance with an existing supplier_invoice_number
        move2 = self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "invoice_date": fields.Date.today() + timedelta(days=-1),
                "ref": "ABC123",
                "invoice_line_ids": [(0, 0, {})],
            }
        )
        with self.assertRaises(ValidationError):
            move2.action_post()
