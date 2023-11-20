# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from gitlab import Gitlab

from odoo import fields, models


class MaintenanceRequest(models.Model):

    _inherit = "maintenance.request"

    gitlab_id = fields.Integer(related="project_id.gitlab_id")
    gitlab_issue_id = fields.Integer(readonly=True, copy=False)
    gitlab_issue_url = fields.Char(readonly=True, copy=False)

    def _gitlab_issue_vals(self):
        return {
            "title": self.name or "",
            "description": self.description or "",
        }

    def send_to_gitlab(self):
        self.ensure_one()
        if not self.gitlab_id or self.gitlab_issue_id:
            return
        token = self.env["ir.config_parameter"].sudo().get_param("gitlab.token", False)
        if not token:
            return
        gl = Gitlab(
            private_token=token,
            url=self.env["ir.config_parameter"].sudo().get_param("gitlab.url", None),
        )
        gl.auth()
        issue = gl.projects.get(self.gitlab_id).issues.create(self._gitlab_issue_vals())
        self.gitlab_issue_id = issue.id
        self.gitlab_issue_url = issue.web_url
