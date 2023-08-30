# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

{
    "name": "GJ Customizations",
    "version": "14.0.1.0.1",
    "author": "NuoBiT Solutions, S.L., Eric Antones",
    "license": "AGPL-3",
    "category": "Custom",
    "website": "https://github.com/oxigensalud/odoo-addons",
    "depends": ["account", "web", "sale", "partner_fax"],
    "data": [
        "views/templates.xml",
        "views/report_templates.xml",
        "views/report_invoice.xml",
        "views/invoice_report_templates.xml",
    ],
    "installable": True,
}
