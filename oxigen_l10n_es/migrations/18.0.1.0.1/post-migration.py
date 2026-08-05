# Copyright NuoBiT Solutions - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)
import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)

# The Dec 2024 map generation joined these six non-deductible members to the
# 303 deductible lines 36/37. Removing those join records from the data file
# stops adding the links on fresh databases, but databases that loaded the old
# file still hold the associations: a data-file deletion never touches
# existing rows, and the modified lines belong to l10n_es_aeat_mod303, so no
# ir.model.data of this module gets garbage-collected either. This one-time
# migration removes the stale links from the two lines.
ND_HOLDER_NAMES = [
    "account_tax_template_p_iva4nd_ic_bc",
    "account_tax_template_p_iva4nd_sp_in",
    "account_tax_template_p_iva10nd_ic_bc",
    "account_tax_template_p_iva10nd_sp_in",
    "account_tax_template_p_iva21nd_ic_bc",
    "account_tax_template_p_iva21nd_sp_in",
]
LINE_XMLIDS = [
    "l10n_es_aeat_mod303.aeat_mod303_2024_10_map_line_36",
    "l10n_es_aeat_mod303.aeat_mod303_2024_10_map_line_37",
]


def migrate(cr, version):
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    for xmlid in LINE_XMLIDS:
        line = env.ref(xmlid, raise_if_not_found=False)
        if not line:
            continue
        holders = line.tax_xmlid_ids.filtered(lambda h: h.name in ND_HOLDER_NAMES)
        if holders:
            line.write({"tax_xmlid_ids": [(3, h.id) for h in holders]})
            _logger.info(
                "Removed %d non-deductible tax links from %s",
                len(holders),
                xmlid,
            )
