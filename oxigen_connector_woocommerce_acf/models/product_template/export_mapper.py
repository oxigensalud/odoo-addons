# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping


class WooCommerceProductTemplateExportMapper(Component):
    _inherit = "woocommerce.product.template.export.mapper"

    @mapping
    def professional_product(self, record):
        return {"professional_product": "1" if record.professional_product else "0"}

    @mapping
    def medical_prescription_required(self, record):
        return {
            "medical_prescription_required": "1"
            if record.medical_prescription_required
            else "0"
        }

    def _get_product_image_attachments(self, record):
        product_image_attachments = super()._get_product_image_attachments(record)
        product_img = record.product_template_image_ids.filtered("video_url")
        return product_image_attachments.filtered(
            lambda x: not any(x.attachment_id.res_id == img.id for img in product_img)
        )
