# Copyright 2023 Dixmit
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo.addons.l10n_es_aeat.tests.test_l10n_es_aeat_mod_base import (
    TestL10nEsAeatModBase,
)

_logger = logging.getLogger("aeat.322")


class TestL10nEsAeatMod322Base(TestL10nEsAeatModBase):
    debug = False
    taxes_sale_2022 = {
        # tax code: (base, tax_amount)
        "S_IVA21S": (1000, 210),
        "S_IVA0": (1000, 0),
    }
    taxes_sale_2023 = {
        # tax code: (base, tax_amount)
        "S_IVA21S": (1000, 210),
        "S_IVA0": (1100, 0),
    }
    taxes_result_12 = {
        # Régimen General - Base imponible 4% Intragrupo
        "1": 0,  # S_IVA4B, S_IVA4S
        # Régimen General - Cuota 4% Intragrupo
        "3": 0,  # S_IVA4B, S_IVA4S
        # Régimen General - Base imponible 10% Intragrupo
        "4": 0,  # S_IVA10B, S_IVA10S
        # Régimen General - Cuota 10% Intragrupo
        "6": 0,  # S_IVA10B, S_IVA10S
        # Régimen General - Base imponible 21%
        # S_IVA21B, S_IVA21S, S_IVA21ISP Intragrupo
        "7": 0,
        # Régimen General - Cuota 21% Intragrupo
        # S_IVA21B, S_IVA21S, S_IVA21ISP
        "9": 0,
        # Modificación bases y cuotas - Base (Compras y ventas)  Resto
        "19": 0,
        # Modificación bases y cuotas - Cuota (Compras y ventas) Resto
        "11": 0,
        # Adq. intracomunitarias de bienes y servicios - Base
        # Régimen General - Base imponible 4% Resto
        "12": 0,  # S_IVA4B, S_IVA4S
        # Régimen General - Cuota 4% Resto
        "14": 0,  # S_IVA4B, S_IVA4S
        # Régimen General - Base imponible 10% Resto
        "15": 0,  # S_IVA10B, S_IVA10S
        # Régimen General - Cuota 10% Resto
        "17": 0,  # S_IVA10B, S_IVA10S
        # Régimen General - Base imponible 21%
        # S_IVA21B, S_IVA21S, S_IVA21ISP Resto
        "18": 0,
        # Régimen General - Cuota 21% Resto
        # S_IVA21B, S_IVA21S, S_IVA21ISP
        "20": 0,
        "21": 0,
        # Adq. intracomunitarias de bienes y servicios - Cuota
        "22": 0,
        # Op. inv. del suj. pasivo (excepto adq. intracom.) - Base
        "23": 0,
        # Op. inv. del suj. pasivo (excepto adq. intracom.) - Cuota
        "24": 0,
        # Modificación bases y cuotas - Base (Compras y ventas)
        "25": 0,
        # Modificación bases y cuotas - Cuota (Compras y ventas)
        "26": 0,
        # Recargo equivalencia - Base imponible 0.5%
        "27": 0,  # S_REQ05
        # Recargo equivalencia - Cuota 0.5%
        "29": 0,  # S_REQ05
        # Recargo equivalencia - Base imponible 1.4%
        "30": 0,  # S_REQ014
        # Recargo equivalencia - Cuota 1.4%
        "32": 0,  # S_REQ014
        # Recargo equivalencia - Base imponible 5.2%
        "33": 0,  # S_REQ52
        # Recargo equivalencia - Cuota 5.2%
        "35": 0,  # S_REQ52
        # Mod. bases y cuotas del recargo de equivalencia - Base
        "36": 0,  # S_REQ05, S_REQ014, S_REQ52
        # Mod. bases y cuotas del recargo de equivalencia - Cuota
        "37": 0,  # S_REQ05, S_REQ014, S_REQ52
        # Cuotas soportadas en op. int. corrientes - Base Intragrupo
        "39": 0,
        # Cuotas soportadas en op. int. corrientes - Cuota Intragrupo
        "40": 0,
        # Cuotas soportadas en op. int. bienes de inversión - Base Intragrupo
        "41": 0,  # P_IVAx_BI
        # Cuotas soportadas en op. int. bienes de inversión - Cuota Intragrupo
        "42": 0,  # P_IVAx_BI
        # Rectificación de deducciones - Base Intragrupo
        "43": 0,
        # Rectificación de deducciones - Cuota intragrupo
        "44": 0,
        # Cuotas soportadas en op. int. corrientes - Base Resto
        "45": 0,
        # Cuotas soportadas en op. int. corrientes - Cuota Resto
        "46": 0,
        # Cuotas soportadas en op. int. bienes de inversión - Base Resto
        "47": 0,  # P_IVAx_BI
        # Cuotas soportadas en op. int. bienes de inversión - Cuota Resto
        "48": 0,  # P_IVAx_BI
        # Cuotas soportadas en las imp. bienes corrientes - Base
        "49": 0,  # P_IVAx_IBC
        # Cuotas soportadas en las imp. bienes corrientes - Cuota
        "50": 0,  # P_IVAx_IBC
        # Cuotas soportadas en las imp. bienes de inversión - Base
        "51": 0,  # P_IVAx_IBI
        # Cuotas soportadas en las imp. bienes de inversión - Cuota
        "52": 0,  # P_IVAx_IBI
        # En adq. intra. de bienes y servicios corrientes - Base
        "53": 0,
        # En adq. intra. de bienes y servicios corrientes - Cuota
        "54": 0,
        # En adq. intra. de bienes de inversión - Base
        "55": 0,  # P_IVAx_IC_BI_1
        # En adq. intra. de bienes de inversión - Cuota
        "56": 0,  # P_IVAx_IC_BI_1
        # Rectificación de deducciones - Base Resto
        "57": 0,
        # Rectificación de deducciones - Cuota Resto
        "58": 0,
        # Compensaciones Rég. especial A. G. y P. - Cuota compras
        "59": 0,
        # Regularización bienes de inversión
        "60": 0,
        # Regularización por aplicación del porcentaje definitivo de prorrata
        "61": 0,
        # Entregas intra. de bienes y servicios - Base ventas
        "71": 0,  # S_IVA0_IC, S_IVA0_SP_I
        # Exportaciones y operaciones asimiladas - Base ventas
        "72": 0,  # S_IVA0_E + S_IVA0
    }
    taxes_asset_purchase = {
        "l10n_es_special_prorate.account_tax_template_p_priva10_bi": (10000, 1000),
    }

    @classmethod
    def _accounts_search(cls):
        codes = {"203000", "280300"}
        for code in codes:
            cls.accounts[code] = cls.env["account.account"].search(
                [("company_id", "=", cls.company.id), ("code", "=", code)]
            )
        return super()._accounts_search()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create model
        cls.company.write({"vat": "1234567890", "l10n_es_prorate_enabled": True})
        cls.prorrate_map_2022 = cls.env["aeat.map.special.prorrate.year"].create(
            {
                "year": 2022,
                "company_id": cls.company.id,
                "tax_percentage": 50,
            }
        )
        cls.model322 = cls.env["l10n.es.aeat.mod322.report"].create(
            {
                "name": "9990000000322",
                "company_id": cls.company.id,
                "company_vat": "1234567890",
                "contact_name": "Test owner",
                "statement_type": "N",
                "support_type": "T",
                "contact_phone": "911234455",
                "year": 2023,
                "period_type": "12",
                "date_start": "2023-12-01",
                "date_end": "2023-12-31",
                "journal_id": cls.journal_misc.id,
            }
        )
        cls.model322_4t = cls.model322.copy(
            {
                "name": "9994000000322",
                "period_type": "12",
                "date_start": "2023-12-01",
                "date_end": "2023-12-31",
            }
        )
        # Purchase invoices
        cls.related_partner = cls.env["res.partner"].create(
            {
                "name": "Related company",
            }
        )
        cls.env["l10n.es.aeat.mod322.group"].create(
            {
                "name": "IVA/2023/23",
                "main_company_id": cls.company.id,
                "vinculated_partner_ids": [(4, cls.related_partner.id)],
            }
        )
        cls.taxes_sale = cls.taxes_sale_2022
        cls._invoice_sale_create("2022-01-01")
        cls.prorrate_map_2022.compute_prorate()
        cls.prorrate_map_2022.close_prorate()
        cls.prorrate_map_2023 = cls.prorrate_map_2022.map_prorrate_next_year_id
        cls.taxes_sale = cls.taxes_sale_2023
        cls._invoice_sale_create("2023-01-01")
        cls.journal_asset = cls.env["account.journal"].create(
            {
                "company_id": cls.company.id,
                "name": "Test journal for sale",
                "type": "general",
                "code": "ASSETS",
            }
        )
        cls.asset_profile = cls.env["account.asset.profile"].create(
            {
                "name": "Assets",
                "journal_id": cls.journal_asset.id,
                "account_asset_id": cls.accounts["203000"].id,
                "account_depreciation_id": cls.accounts["280300"].id,
                "account_expense_depreciation_id": cls.accounts["280300"].id,
                "capital_asset_type_id": cls.env.ref(
                    "l10n_es_account_capital_asset.account_capital_asset_type_data_normal"
                ).id,
            }
        )
        cls.invoice_asset = cls._invoice_asset_create("2022-01-01")
        cls.asset = cls.invoice_asset.invoice_line_ids.asset_id
        cls.asset.validate()

    @classmethod
    def _invoice_asset_create(cls, dt, extra_vals=None):
        data = {
            "company_id": cls.company.id,
            "partner_id": cls.supplier.id,
            "invoice_date": dt,
            "move_type": "in_invoice",
            "journal_id": cls.journal_purchase.id,
            "invoice_line_ids": [],
        }
        _logger.debug("Creating purchase invoice for asset: date = %s" % dt)
        if cls.debug:
            _logger.debug("{:>14} {:>9}".format("PURCHASE TAX", "PRICE"))
        for desc, values in cls.taxes_asset_purchase.items():
            if cls.debug:
                _logger.debug("{:>14} {:>9}".format(desc, values[0]))
            # Allow to duplicate taxes skipping the unique key constraint
            line_data = {
                "name": "Test for tax(es) %s" % desc,
                "account_id": cls.accounts["600000"].id,
                "price_unit": values[0],
                "quantity": 1,
                "asset_profile_id": cls.asset_profile.id,
            }
            taxes = cls._get_taxes(desc.split("//")[0])
            if taxes:
                line_data["tax_ids"] = [(4, t.id) for t in taxes]
            data["invoice_line_ids"].append((0, 0, line_data))
        if extra_vals:
            data.update(extra_vals)
        inv = cls.env["account.move"].with_user(cls.billing_user).create(data)
        inv.sudo().action_post()  # FIXME: Why do we need to do it as sudo?
        if cls.debug:
            cls._print_move_lines(inv.line_ids)
        return inv

    def _check_tax_lines(self):
        for field, result in iter(self.taxes_result.items()):
            _logger.debug("Checking tax line: %s" % field)
            lines = self.model322.tax_line_ids.filtered(
                lambda x: x.field_number == int(field)
            )
            self.assertAlmostEqual(
                sum(lines.mapped("amount")),
                result,
                2,
                "Incorrect result in field %s" % field,
            )

    def test_calculate_last_period(self):
        self.prorrate_map_2023.compute_prorate()
        self.prorrate_map_2023.close_prorate()
        self.model322.button_calculate()
        self.model322.invalidate_cache()
        for field, result in iter(self.taxes_result_12.items()):
            _logger.debug("Checking tax line: %s" % field)
            lines = self.model322.tax_line_ids.filtered(
                lambda x: x.field_number == int(field)
            )
            self.assertAlmostEqual(
                sum(lines.mapped("amount")),
                result,
                2,
                "Incorrect result in field %s" % field,
            )
