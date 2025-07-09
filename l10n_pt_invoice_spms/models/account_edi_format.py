# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class AccountEdiFormat(models.Model):

    _inherit = "account.edi.format"

    def _get_xml_builder(self, company):
        """Override to return the SPMS XML builder."""
        if self.code == "spms_cius_pt_211" and company.country_id.code == "PT":
            return self.env["account.edi.xml.spms_cius_pt_211"]
        return super()._get_xml_builder(company)


class AccountEdiXmlSpmsCiusPt211(models.AbstractModel):
    _name = "account.edi.xml.spms_cius_pt_211"
    _inherit = "account.edi.xml.cius_pt_211"

    def _export_invoice_vals(self, invoice):
        # EXTENDS account.edi.xml.ubl_20
        vals = super()._export_invoice_vals(invoice)

        vals.update(
            {
                "InvoiceType_template": "l10n_pt_invoice_spms.spms_cius_pt_211_InvoiceType",
                "InvoiceExtension_spms": "l10n_pt_invoice_spms.spms_cius_pt_211_InvoiceExtension_spms",  # noqa: disable=B950
            }
        )
        lots = invoice.invoice_line_ids.product_id.spms_lot_id
        lotes = []
        for lot in lots:
            lines = invoice.invoice_line_ids.filtered(
                lambda l: l.product_id.spms_lot_id == lot
            )
            lotes.append(
                {
                    "numero": lot.name,
                    "tipo": lot.lot_type,
                    "amount": sum(lines.mapped("price_subtotal")),
                    "total": len(lines),
                    "dispensas": [
                        {
                            "prescription": line.spms_prescription,
                            "user_number": line.spms_user_number,
                            "beneficiary_number": line.spms_beneficiary_number,
                            "prescription_type": line.spms_prescription_type_id.code,
                            "price_subtotal": line.price_subtotal,
                            "price_unit": line.price_unit,
                            "quantity": line.quantity,
                            "context": line.spms_context_id.code,
                            "line_number": line.id,
                            "system": line.product_id.default_code,
                            "suspension_reason": line.spms_suspension_reason_id.code,
                            "start_date": line.spms_start_date
                            and line.spms_start_date.isoformat(),
                            "end_date": line.spms_end_date
                            and line.spms_end_date.isoformat(),
                        }
                        for line in lines
                    ],
                }
            )
        vals["vals"].update(
            {
                "spms_crd_vals": {
                    "valor_total_prestacoes": invoice.amount_total,
                    "currency_dp": invoice.currency_id.decimal_places,
                    "quantidade_total_prestacoes": len(invoice.invoice_line_ids),
                    "numero_lotes": len(lots),
                    "lotes": lotes,
                },
            }
        )

        return vals
