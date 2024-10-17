# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import mapping
from odoo.addons.connector_extension.common import tools


class WooCommerceProductTemplateExportMapper(Component):
    _inherit = "woocommerce.product.template.export.mapper"

    def _get_product_additional_information(self, record):
        if not record.technical_features:
            return False
        return tools.color_rgb2hex(record.technical_features)

    @mapping
    def additional_information(self, record):
        additional_information = []
        technical_features = self._get_product_additional_information(record)
        if technical_features:
            additional_information.append(technical_features)
        return {"additional_information": "\n".join(additional_information) or None}
