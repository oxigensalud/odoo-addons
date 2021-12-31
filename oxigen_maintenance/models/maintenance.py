# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = "maintenance.equipment"

    location_id = fields.Many2one("stock.location", string="Location")
    # Rename standard `location` label to not have duplicated labels
    location = fields.Char(string="Used in location")

    def _prepare_request_from_plan(self, maintenance_plan, next_maintenance_date):

        res = super(MaintenanceEquipment, self)._prepare_request_from_plan(
            maintenance_plan, next_maintenance_date
        )
        kind = maintenance_plan.maintenance_kind_id.name or _("Unspecified kind")
        res["name"] = _("%s - %s - %s") % (kind, self.name, maintenance_plan.name)
        return res
