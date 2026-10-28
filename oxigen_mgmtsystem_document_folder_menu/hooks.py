# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os

from lxml import etree

from odoo.tools import file_open
from odoo.tools.safe_eval import safe_eval

MODULE = "oxigen_mgmtsystem_document_folder_menu"


def _manuals_context(env):
    """The context this module gives the Manuals action, evaluated from its
    data file. A category deleted since then is evaluated as False."""
    with file_open(
        os.path.join(MODULE, "views/document_page_views.xml"), "rb"
    ) as data_file:
        (expression,) = etree.parse(data_file).xpath(
            "//record[@id='mgmtsystem_manual.action_manuals']"
            "/field[@name='context']/@eval"
        )
    return safe_eval(expression, {"ref": env["ir.model.data"]._xmlid_to_res_id})


def uninstall_hook(env):
    """Give the Manuals action back the default context it has without this
    module, which no update of mgmtsystem_manual writes, as its action sets
    none. Only while the action still holds this module's context: one
    edited while the module was installed keeps the edit."""
    action = env.ref("mgmtsystem_manual.action_manuals")
    if safe_eval(action.context) == _manuals_context(env):
        action.context = action.default_get(["context"])["context"]
