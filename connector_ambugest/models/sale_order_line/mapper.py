# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)


from odoo.addons.component.core import Component
from odoo.addons.connector.components.mapper import convert, mapping, only_create


class SaleOrderLineImportMapper(Component):
    _name = "ambugest.sale.order.line.import.mapper"
    _inherit = "ambugest.import.mapper"
    _apply_on = "ambugest.sale.order.line"

    direct = [
        ("EMPRESA", "ambugest_empresa"),
        ("Fecha_Servicio", "ambugest_fecha_servicio"),
        ("Codigo_Servicio", "ambugest_codigo_servicio"),
        ("Servicio_Dia", "ambugest_servicio_dia"),
        ("Servicio_Ano", "ambugest_servicio_ano"),
        ("Articulo", "ambugest_articulo"),
        (convert("Cantidad", float), "product_uom_qty"),
    ]

    @only_create
    @mapping
    def backend_id(self, record):
        return {"backend_id": self.backend_record.id}

    @mapping
    def product(self, record):
        external_id = (record["EMPRESA"], record["Articulo"])

        binder = self.binder_for("ambugest.product.product")
        product = binder.to_internal(external_id, unwrap=True)
        assert product, (
            f"product_id {external_id} should have been "
            f"imported in ProductProductImporter._import_dependencies"
        )

        return {"product_id": product.id}
