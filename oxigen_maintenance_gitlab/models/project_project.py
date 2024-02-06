# Copyright 2023 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProjectProject(models.Model):

    _inherit = "project.project"

    gitlab_id = fields.Integer(help="Id of the project for gitlab", copy=False)
