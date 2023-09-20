from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSupplierInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)

        # ENVIRONMENTS
        cls.account_account = cls.env["account.account"]
        cls.account_move = cls.env["account.move"].with_context(
            {"tracking_disable": True}
        )

        # INSTANCES
        cls.partner = cls.env.ref("base.res_partner_2")
        # Account for invoice
        cls.account = cls.account_account.search(
            [
                (
                    "user_type_id",
                    "=",
                    cls.env.ref("account.data_account_type_receivable").id,
                )
            ],
            limit=1,
        )
        # Invoice with unique reference 'ABC123'
        cls.invoice = cls.account_move.create(
            {
                "partner_id": cls.partner.id,
                "invoice_date": fields.Date.today(),
                "move_type": "in_invoice",
                "ref": "ABC123",
                "invoice_line_ids": [(0, 0, {"partner_id": cls.partner.id})],
            }
        )

    def test_check_unique_supplier_invoice_number_insensitive(self):
        # A new invoice instance with an existing supplier_invoice_number
        with self.assertRaises(ValidationError):
            self.account_move.create(
                {
                    "partner_id": self.partner.id,
                    "move_type": "in_invoice",
                    "ref": "ABC123",
                }
            )
        # A new invoice instance with a new supplier_invoice_number
        self.account_move.create(
            {
                "partner_id": self.partner.id,
                "move_type": "in_invoice",
                "ref": "ABC123bis",
            }
        )
