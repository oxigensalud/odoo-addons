# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import changed_by, mapping


class WooCommerceProductTemplateExportMapper(Component):
    _inherit = "woocommerce.product.export.mapper"

    # This function is used to export meta_data
    @mapping
    def meta_data(self, record):
        # fields must have been created on woocommerce
        return {
            "meta_data": [
                {
                    "key": "professional_product", "value": "1" if record.professional_product else "0"
                },
                {
                    "key": "medical_prescription_required",
                    "value": "1" if record.medical_prescription_required else "0"
                }
            ]
        }
