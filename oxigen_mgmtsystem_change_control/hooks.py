# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, api


def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    menu = env.ref("mgmtsystem_review.menu_open_review", raise_if_not_found=False)
    if menu:
        menu.write({"active": True})

    env["ir.translation"].search(
        [("module", "=", "oxigen_mgmtsystem_change_control")]
    ).unlink()
