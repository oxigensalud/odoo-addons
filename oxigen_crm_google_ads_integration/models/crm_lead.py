# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import fields, models


class Lead(models.Model):
    _inherit = "crm.lead"

    google_ads_data = fields.Text()

    def create_google_ads_lead(self, request_data, uid):
        """Create a Lead from Google Ads Form"""
        vals = self.prepare_lead_vals(request_data["user_column_data"], uid)
        new_lead = self.env["crm.lead"].with_user(uid).sudo().create(vals)
        # transform id fields to their names
        vals["partner_id"] = self.env["res.partner"].browse(vals["partner_id"]).name
        vals["country_id"] = self.env["res.country"].browse(vals["country_id"]).name
        vals["id"] = new_lead.id
        # keep all received values in new field google_ads_data
        new_lead.with_user(uid).sudo().update({"google_ads_data": vals})
        return ("CRM Lead with the following data Successfully created!", vals)

    def prepare_lead_vals(self, data, uid):
        new_dict = {}
        for field in data:
            new_dict[field["column_id"]] = field["string_value"]
        country = self.get_country(new_dict.get("COUNTRY", ""))
        city = new_dict.get("CITY", "")
        partner = self.get_or_create_partner(
            uid, new_dict.get("COMPANY_NAME", ""), country, city
        )
        return {
            "description": "Lead Created from Google Ads",
            "contact_name": new_dict.get("FULL_NAME", "")
            or new_dict.get("FIRST_NAME ", "") + new_dict.get("LAST_NAME ", ""),
            "partner_id": partner.id,
            "type": "lead",
            # address
            "street": new_dict.get("STREET_ADDRESS", ""),
            "country_id": country.id,
            "city": city,
            "zip": new_dict.get("POSTAL_CODE", ""),
            # other contact fields
            "function": new_dict.get("JOB_TITLE", ""),
            # specific contact fields
            "email_from": new_dict.get("EMAIL", ""),
            "phone": new_dict.get("PHONE_NUMBER", ""),
            # questions
            # Which product/service are you interested in?
            "name": new_dict.get("PRODUCT", "") or new_dict.get("SERVICE", ""),
        }

    def get_country(self, str_country):
        if str_country in ("Espanya", "España", "Spain"):
            return self.env["res.country"].search([("code", "=", "ES")])
        country = self.env["res.country"].search([("name", "=", str_country)])
        if country:
            return country
        return self.env["res.country"]

    def get_or_create_partner(self, uid, name, country, city):
        partner = self.env["res.partner"]
        existing_partner = partner.sudo().search([("name", "=", name)], limit=1)
        if existing_partner:
            return existing_partner
        else:
            return (
                partner.sudo()
                .with_user(uid)
                .create({"name": name, "country_id": country.id, "city": city})
            )
