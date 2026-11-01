# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import csv

from odoo.tools import file_open


def post_init_hook(env):
    companies = env["res.company"].search(
        [("chart_template", "like", "es_%")],
        order="parent_path",
    )
    current_taxes = (
        env["account.tax"]
        .with_context(active_test=False)
        .search(env["account.tax"]._check_company_domain(companies))
    )
    tax_map = {
        xmlid: record_id
        for record_id, xmlid in current_taxes.get_external_id().items()
        if xmlid
    }
    with file_open(
        "oxigen_l10n_es_account_asset_tax_consistency"
        "/data/template/account.tax-es_common_mainland.csv"
    ) as template_file:
        for record in csv.DictReader(template_file):
            for company in companies:
                xmlid = f"account.{company.id}_{record['id']}"
                record_id = tax_map.get(xmlid)
                if record_id:
                    env["account.tax"].browse(record_id).write(
                        {"apply_to_asset": record["apply_to_asset"]}
                    )
