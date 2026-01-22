# Copyright 2022 ForgeFlow S.L.
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Delivery MRW receipt",
    "summary": "Customizations for Oxigen for MRW incoming shipments",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, NuoBiT Solutions SL",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "category": "Stock",
    "depends": ["oxigen_delivery_mrw"],
    "license": "AGPL-3",
    "data": [
        "views/stock_picking.xml",
        "wizards/stock_number_package_validated_wizard_views.xml",
    ],
}
