# Copyright 2026 NuoBiT Solutions SL - Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from openupgradelib import openupgrade

from odoo import fields

from odoo.addons.connector_woocommerce.common.tools import is_blank_html

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    now = fields.Datetime.now()
    backends = env["woocommerce.backend"].with_context(active_test=False).search([])
    for backend in backends:
        templates = (
            env["woocommerce.product.template"]
            .with_context(active_test=False)
            .search([("backend_id", "=", backend.id)])
            .odoo_id
        )
        for language in backend.lang_ids:
            blank_templates = templates.with_context(lang=language.code).filtered(
                lambda product: bool(product.technical_features)
                and is_blank_html(product.technical_features)
            )
            # A variable template is exported as a dependency of its variants.
            # Mark both sides so the normal batch domains select the right one.
            for products in (blank_templates, blank_templates.product_variant_ids):
                products.woocommerce_write_date = now
                _logger.info(
                    "Blank technical features re-export: backend %s, language %s, "
                    "%s: %s records",
                    backend.id,
                    language.code,
                    products._name,
                    len(products),
                )
                _logger.debug(
                    "Blank technical features re-export: backend %s, language %s, "
                    "%s IDs: %s",
                    backend.id,
                    language.code,
                    products._name,
                    products.ids,
                )
