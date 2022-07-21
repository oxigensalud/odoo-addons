import requests

from odoo import http
from odoo.exceptions import AccessDenied


class GoogleAdsController(http.Controller):
    @http.route("/googleforms/inbox", auth="public", type="json")
    def google_ads_receive_data(self):
        if not http.request.session.sid:
            return http.redirect_with_hash("/web/login")
        session = http.request.session
        if session and http.request.httprequest.method == "POST":
            request_data = http.request.jsonrequest
            key = request_data.get("google_key")
            if key:
                checked_credentials = http.request.env[
                    "res.users.apikeys"
                ]._check_credentials(key=key, scope="Google Ads")
                if checked_credentials:
                    url = (
                        http.request.env["ir.config_parameter"]
                        .sudo()
                        .get_param("oxigen_intermediate_connector.connection_url", "")
                        + "/googleforms/submit"
                    )
                    payload = http.request.jsonrequest
                    payload["google_key"] = (
                        http.request.env["ir.config_parameter"]
                        .sudo()
                        .get_param("oxigen_intermediate_connector.api_key", "")
                    )
                    headers = {
                        "Content-Type": "application/json",
                    }
                    response = requests.request(
                        "POST", url, json=payload, headers=headers
                    )

                    return response.text
        raise AccessDenied()
