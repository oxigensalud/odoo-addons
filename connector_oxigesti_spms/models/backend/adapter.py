# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import logging

from odoo.addons.component.core import Component

_logger = logging.getLogger(__name__)


class OxigestiSPMSBackendAdapter(Component):
    _name = "oxigesti.spms.backend.adapter"
    _inherit = "oxigesti.spms.adapter"
    _description = "Oxigesti SPMS Backend Adapter"

    _apply_on = "oxigesti.spms.backend"
