# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging

from openupgradelib import openupgrade

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    _logger.info("Emptying mrp_type fields in lots that are not related with a product")

    all_lots = env["stock.production.lot"].search(
        [("product_id.mrp_type", "!=", False)]
    )
    for lot in all_lots:
        vals = {}
        for field in lot.get_all_product_mrp_fields():
            if field not in lot.mrp_fields_allowed and lot[field]:
                vals[field] = False
        if vals:
            lot.write(vals)
            _logger.info("Updated lot %s with values %s", lot.id, vals)
