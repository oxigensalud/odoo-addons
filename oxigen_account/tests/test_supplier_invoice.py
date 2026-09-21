# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

from odoo.exceptions import ValidationError
from odoo.tests import Form, tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestSupplierInvoice(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls, chart_template_ref=None):
        super().setUpClass(chart_template_ref=chart_template_ref)
        cls.partner_a.property_supplier_payment_term_id = False

    def _create_invoice(self, reference):
        with Form(
            self.env["account.move"].with_context(default_move_type="in_invoice")
        ) as form:
            form.partner_id = self.partner_a
            form.invoice_date = "2017-01-01"
            form.ref = reference
            with form.invoice_line_ids.new() as line:
                line.product_id = self.product_a
                line.price_unit = 100
        invoice = form.save()
        self.env["ir.attachment"].create(
            {
                "name": reference + ".txt",
                "datas": base64.b64encode(b"Synthetic invoice attachment"),
                "res_model": "account.move",
                "res_id": invoice.id,
                "mimetype": "text/plain",
            }
        )
        return invoice

    def test_duplicate_supplier_reference(self):
        invoice = self._create_invoice("TEST-REF")
        invoice.action_post()
        duplicate = self._create_invoice("TEST-REF")
        with self.assertRaises(ValidationError):
            duplicate.action_post()
        other = self._create_invoice("TEST-OTHER")
        other.action_post()
        self.assertEqual(other.state, "posted")
