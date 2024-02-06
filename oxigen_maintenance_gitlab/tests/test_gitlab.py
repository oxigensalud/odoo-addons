# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import responses

from odoo.tests.common import SavepointCase


class TestGitlab(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.project = cls.env["project.project"].create(
            {
                "name": "AUX",
                "gitlab_id": 1,
            }
        )

        cls.request = cls.env["maintenance.request"].create(
            {
                "name": "name",
                "description": "DESCRIPTION",
            }
        )
        cls.server = "http://localhost"
        cls.env["ir.config_parameter"].sudo().set_param("gitlab.url", cls.server)

    def test_no_sending_no_token(self):
        self.request.project_id = self.project
        self.request.send_to_gitlab()
        self.assertFalse(self.request.gitlab_issue_id)
        self.assertFalse(self.request.gitlab_issue_url)

    def test_no_sending_missing_project(self):
        self.env["ir.config_parameter"].sudo().set_param("gitlab.token", "TOKEN")
        self.request.send_to_gitlab()
        self.assertFalse(self.request.gitlab_issue_id)
        self.assertFalse(self.request.gitlab_issue_url)

    @responses.activate
    def test_sending_task(self):
        self.env["ir.config_parameter"].sudo().set_param("gitlab.token", "TOKEN")
        self.request.project_id = self.project
        responses.add(
            method=responses.GET,
            url="http://localhost/api/v4/user",
            json={
                "id": 1,
                "username": "username",
                "web_url": "http://localhost/username",
            },
            status=200,
        )
        responses.add(
            method=responses.GET,
            url="http://localhost/api/v4/projects/1",
            json={
                "name": "DEMO Project",
                "id": 1,
            },
            status=200,
        )
        responses.add(
            method=responses.POST,
            url="http://localhost/api/v4/projects/1/issues",
            json={
                "name": "DEMO Project",
                "id": 1,
                "web_url": "https://localhost/1/issues/1",
            },
            status=200,
        )
        self.request.send_to_gitlab()
        self.assertTrue(self.request.gitlab_issue_id)
        self.assertTrue(self.request.gitlab_issue_url)
