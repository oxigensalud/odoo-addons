# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import Component


class WooCommerceWPMLProductTemplateAdapter(Component):
    _inherit = "woocommerce.product.template.adapter"

    def prepare_meta_data(self, data):
        video_gallery_fields = [k for k in data.keys() if k.startswith("video_gallery")]
        if video_gallery_fields:
            self.env.context = {"video_gallery_fields": video_gallery_fields}
        return super(WooCommerceWPMLProductTemplateAdapter, self).prepare_meta_data(
            data
        )

    def _prepare_meta_data_fields(self):
        meta_data_fields = super()._prepare_meta_data_fields()
        meta_data_fields.extend(["additional_information"])
        video_gallery_fields = self.env.context.get("video_gallery_fields", {})
        if video_gallery_fields:
            meta_data_fields.extend(video_gallery_fields)
        return meta_data_fields
