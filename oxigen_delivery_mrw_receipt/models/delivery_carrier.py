# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class DeliveryCarrier(models.Model):
    _inherit = "delivery.carrier"

    def _prepare_mrw_shipping(self, picking):
        res = super()._prepare_mrw_shipping(picking)
        sending_partner = picking.partner_id
        receiving_partner = picking.location_dest_id.get_warehouse().partner_id
        if picking.picking_type_code == "incoming":
            res["DatosRecogida"] = {
                "Direccion": self.mrw_address(
                    sending_partner, self.international_shipping
                ),
                "Nif": sending_partner.vat or "",
                "Nombre": sending_partner.name,
                "Telefono": sending_partner.phone or "",
            }
            res["DatosEntrega"] = {
                "Direccion": self.mrw_address(
                    receiving_partner, self.international_shipping
                ),
                "Nif": receiving_partner.vat or "",
                # if module added to OCA, this field is custom for Oxigen
                "Nombre": receiving_partner.parent_id.name
                if receiving_partner.parent_id
                else receiving_partner.name,
                "Telefono": receiving_partner.phone or "",
                "ALaAtencionDe": "",
                "Observaciones": picking.note or "",
            }
        return res
