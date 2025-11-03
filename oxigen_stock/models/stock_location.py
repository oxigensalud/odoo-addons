# Copyright 2022 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class StockLocation(models.Model):
    _inherit = "stock.location"

    name = fields.Char(translate=True)

    display_name = fields.Char(
        compute="_compute_display_name",
        recursive=True,
        store=True,
    )

    @api.depends("name", "location_id.complete_name")
    def _compute_complete_name(self):
        # we set the method as in v11 where complete_name has the full path
        """Forms complete name of location from parent location to child location."""
        for location in self:
            if location.location_id.complete_name:
                location.complete_name = (
                    f"{location.location_id.complete_name}" f"/{location.name}"
                )
            else:
                location.complete_name = location.name

    @api.depends("name", "location_id", "location_id.display_name", "usage")
    def _compute_display_name(self):
        """Compute display name as hierarchical path, skipping 'view' usage."""
        for location in self:
            name = location.name or ""
            current_location = location
            while current_location.location_id and current_location.usage != "view":
                current_location = current_location.location_id
                if not name:
                    raise UserError(_("You have to set a name for this location."))
                name = f"{current_location.name}/{name}"
            location.display_name = name
