# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import Component


class OXigestiSPMSAccountInvoiceListener(Component):
    _name = "oxigesti.spms.account.invoice.listener"
    _inherit = "base.event.listener"

    _apply_on = "account.move"

    def on_validate_out_invoice(self, record):
        record.ensure_one()
        for order in record.invoice_line_ids.sale_line_ids.order_id:
            bindings = order.oxigesti_spms_bind_ids
            if bindings:
                other_invoices = order.invoice_ids.filtered(
                    lambda inv: inv != record
                    and inv.state == "posted"
                    and inv.move_type == "out_invoice"
                )
                if other_invoices:
                    raise UserError(
                        _(
                            "This invoice cannot be validated because the "
                            "associated sales order already has related invoice lines. "
                            "Please review the sales order and ensure it does "
                            "not have any existing invoices linked before proceeding."
                        )
                    )
                for binding in bindings:
                    binding.export_invoice_data(record)

    def on_cancel_out_invoice(self, record):
        record.ensure_one()
        for order in record.invoice_line_ids.mapped("sale_line_ids.order_id"):
            for binding in order.oxigesti_spms_bind_ids:
                binding.export_invoice_data(record, clear=True)
