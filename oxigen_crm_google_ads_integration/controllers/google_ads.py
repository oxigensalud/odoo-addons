from odoo import http
from odoo.exceptions import AccessDenied

# on install: change user_id of api key to google ads user


class GoogleAdsController(http.Controller):
    @http.route("/googleforms/submit", auth="public", type="json")
    def google_ads_lead_data(self):
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
                    return (
                        http.request.env["crm.lead"]
                        .with_delay()
                        .create_google_ads_lead(request_data, checked_credentials)
                    )
        raise AccessDenied()
