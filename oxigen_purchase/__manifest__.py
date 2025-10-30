# Copyright 2021 ForgeFlow S.L.
# Copyright 2025 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Oxigen Purchase",
    "summary": "Customizations for Oxigen in Purchase application",
    "version": "18.0.1.0.0",
    "author": "ForgeFlow, NuoBiT Solutions SL",
    "website": "https://github.com/OCA/oxigen.odo-adodns",
    "category": "Purchases",
    "depends": [
        "purchase_stock",
        "stock_picking_partner_ref",
        "purchase_tier_validation",
        "sale_stock",
    ],
    "license": "AGPL-3",
    "data": ["views/purchase_views.xml"],
}
