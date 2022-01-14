# Copyright 2021 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Oxigen Partner Grouping Criteria",
    "summary": "Customizations for Oxigen. This modules moves the 'Sales Invoicing "
    "Grouping Criteria' field in the partner view",
    "version": "14.0.1.0.0",
    "author": "ForgeFlow",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "category": "Sales Management",
    "depends": ["sale_order_invoicing_grouping_criteria"],
    "installable": True,
    "license": "AGPL-3",
    "data": ["views/res_partner_views.xml"],
}
