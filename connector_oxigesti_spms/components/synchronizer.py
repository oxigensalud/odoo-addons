# Copyright 2025 NuoBiT - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo.addons.component.core import AbstractComponent


class OxigestiSPMSSynchronizer(AbstractComponent):
    _name = "oxigesti.spms.synchronizer"
    _inherit = ["connector.extension.synchronizer", "oxigesti.spms.connector"]

    _description = "Oxigesti SPMS Synchronizer Component"
