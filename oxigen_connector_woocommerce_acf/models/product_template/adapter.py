# Copyright NuoBiT Solutions - Kilian Niubo <kniubo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceProductTemplateAdapter(Component):
    _inherit = "woocommerce.product.template.adapter"

    def _prepare_meta_data_fields(self):
        meta_data_fields = super()._prepare_meta_data_fields()
        meta_data_fields.extend(
            ["professional_product", "medical_prescription_required"]
        )
        return meta_data_fields
