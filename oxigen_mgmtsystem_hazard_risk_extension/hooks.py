# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import os

from lxml import etree

from odoo import SUPERUSER_ID, api
from odoo.tools import file_open

MODULE = "oxigen_mgmtsystem_hazard_risk_extension"


def _external_id(module_name, xml_id):
    """The complete external id of an id written in a data file of the
    module, as the data loader completes it."""
    return xml_id if "." in xml_id else "%s.%s" % (module_name, xml_id)


def _formula_descriptions(module_name, filename):
    """The description that each risk formula of a data file of the module
    sets, by external id."""
    with file_open(os.path.join(module_name, filename), "rb") as data_file:
        records = etree.parse(data_file).xpath(
            "//record[@model='mgmtsystem.hazard.risk.computation']"
        )
    return {
        _external_id(module_name, record.get("id")): record.findtext(
            "field[@name='description']"
        )
        for record in records
    }


def _restore_formula_descriptions(env):
    """Give back the stock English description to each risk formula this
    module relabels, if it still exists and still holds this module's text:
    there is nothing to give back to a formula a manager deleted, and one
    edited while the module was installed keeps the edit."""
    stock = _formula_descriptions(
        "mgmtsystem_hazard_risk", "data/mgmtsystem_hazard_risk_computation.xml"
    )
    relabelled = _formula_descriptions(
        MODULE, "data/mgmtsystem_hazard_risk_computation_data.xml"
    )
    for xml_id, description in relabelled.items():
        formula = env.ref(xml_id, raise_if_not_found=False)
        if formula is not None and formula.description == description:
            formula.description = stock[xml_id]


def post_init_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env["ir.translation"]._force_module_terms(MODULE)


def uninstall_hook(cr, _registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _restore_formula_descriptions(env)
    env["ir.translation"]._delete_module_terms(MODULE)
    module = env["ir.module.module"].search([("name", "=", MODULE)])
    module.ensure_one()
    module.dependencies_id.depend_id._update_translations()
