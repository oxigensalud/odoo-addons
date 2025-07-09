# Copyright 2020 Creu Blanca
# @author: Enric Tobella
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64

import xmlsig
from lxml import etree
from OpenSSL import crypto

from odoo import _
from odoo.exceptions import UserError

from odoo.addons.component.core import Component


class EdiOutputL10nEsFacturae(Component):
    _name = "edi.output.generate.l10n_pt_spms"
    _inherit = "edi.component.output.mixin"
    _usage = "output.generate"
    _backend_type = "l10n_pt_spms"

    def generate(self):
        invoice = self.exchange_record.record
        edi_format = self.env.ref("l10n_pt_invoice_spms.spms_edi_format")
        builder = edi_format._get_xml_builder(invoice.company_id)
        xml_content, errors = builder._export_invoice(invoice)
        if errors:
            raise UserError(_("Errors while generating XML: %s" % errors))

        einvoice = etree.fromstring(xml_content)

        extensions = einvoice.find(
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtensions"  # noqa: disable=B950
        )
        if extensions is None:
            extensions = etree.Element(
                "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtensions"  # noqa: disable=B950
            )
            einvoice.insert(0, extensions)

        extension = etree.Element(
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}UBLExtension"  # noqa: disable=B950
        )
        extensions.insert(0, extension)
        etree.SubElement(
            extension,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}ExtensionURI",  # noqa: disable=B950
        ).text = "urn:oasis:names:specification:ubl:dsig:enveloped"
        extension_content = etree.SubElement(
            extension,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2}ExtensionContent",  # noqa: disable=B950
        )
        signature_information = etree.SubElement(
            extension_content,
            "{urn:oasis:names:specification:ubl:schema:xsd:CommonSignatureComponents-2}UBLDocumentSignatures",  # noqa: disable=B950d
        )
        sign = xmlsig.template.create(
            c14n_method=xmlsig.constants.TransformExclC14NWithComments,
            sign_method=xmlsig.constants.TransformRsaSha1,
            ns="ds",
        )
        ref = xmlsig.template.add_reference(
            sign, xmlsig.constants.TransformSha1, uri=""
        )
        xmlsig.template.add_transform(ref, xmlsig.constants.TransformEnveloped)
        key_info = xmlsig.template.ensure_key_info(sign)
        x509_data = xmlsig.template.add_x509_data(key_info)
        xmlsig.template.x509_data_add_certificate(x509_data)
        ctx = xmlsig.SignatureContext()
        key = crypto.load_pkcs12(
            base64.b64decode(invoice.company_id.sudo().spms_certificate),
            invoice.company_id.sudo().spms_certificate_password,
        )
        ctx.x509 = key.get_certificate().to_cryptography()
        ctx.public_key = ctx.x509.public_key()
        ctx.private_key = key.get_privatekey().to_cryptography_key()

        # In order to make it work, we sign in the root and we move later on
        # the signature to the right place. This is because the signature must
        # be in the UBLDocumentSignatures element, but xmlsig does not allow to
        # sign an element that is not in the root.
        einvoice.append(sign)
        ctx.sign(sign)
        einvoice.remove(sign)
        signature_information.append(sign)
        return etree.tostring(einvoice, xml_declaration=True, encoding="UTF-8")
