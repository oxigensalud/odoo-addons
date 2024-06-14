# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MaintenanceEquipmentOperatingSystem(models.Model):

    _name = "maintenance.equipment.operating.system"
    _description = "Operating System"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
