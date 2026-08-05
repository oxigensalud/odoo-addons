# Copyright 2026 NuoBiT Solutions SL - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import models

from odoo.addons.account.models.chart_template import template

from ..hooks import _create_fiscal_position_tax_mappings


class AccountChartTemplate(models.AbstractModel):
    _inherit = "account.chart.template"

    @template("es_full")
    def _get_es_full_oxigen_template_data(self):
        return {
            "code_digits": 9,
        }

    @template("es_common", "account.account")
    def _get_es_common_oxigen_account_account(self):
        return self._parse_csv(
            "es_common",
            "account.account",
            module="oxigen_l10n_es",
        )

    @template("es_common_mainland", "account.tax.group")
    def _get_es_common_mainland_oxigen_tax_group(self):
        return self._parse_csv(
            "es_common_mainland",
            "account.tax.group",
            module="oxigen_l10n_es",
        )

    @template("es_common_mainland", "account.tax")
    def _get_es_common_mainland_oxigen_tax_data(self):
        tax_data = self._parse_csv(
            "es_common_mainland",
            "account.tax",
            module="oxigen_l10n_es",
        )
        self._deref_account_tags("es_pymes", tax_data)
        return tax_data

    @template("es_common_mainland", "account.fiscal.position")
    def _get_es_common_mainland_oxigen_fiscal_position(self):
        return self._parse_csv(
            "es_common_mainland",
            "account.fiscal.position",
            module="oxigen_l10n_es",
        )

    def _post_load_data(self, template_code, company, template_data):
        res = super()._post_load_data(template_code, company, template_data)
        _create_fiscal_position_tax_mappings(
            self.env,
            company or self.env.company,
        )
        return res
