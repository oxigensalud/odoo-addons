# Copyright 2023 Dixmit
# License AGPL-3 - See https://www.gnu.org/licenses/agpl-3.0

import logging

from odoo import exceptions

from odoo.addons.l10n_es_aeat.tests.test_l10n_es_aeat_mod_base import (
    TestL10nEsAeatModBase,
)

_logger = logging.getLogger("aeat.322")


class TestL10nEsAeatMod322Base(TestL10nEsAeatModBase):
    debug = False
    taxes_sale = {
        # tax code: (base, tax_amount)
        "S_IVA21S": (1000, 210),
        "S_IVA0": (1000, 0),
    }
    taxes_purchase = {
        # tax code: (base, tax_amount)
        "l10n_es_special_prorate.account_tax_template_p_priva10_bc": (1000, 100),
    }
    taxes_result = {
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
        "7": 1000,
        # Régimen General - Cuota 21% Intragrupo
        # S_IVA21B, S_IVA21S, S_IVA21ISP
        "9": 210,
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
        "18": 1000 + 1000,
        # Régimen General - Cuota 21% Resto
        # S_IVA21B, S_IVA21S, S_IVA21ISP
        "20": 210 + 210,
        "21": 0,
        # Adq. intracomunitarias de bienes y servicios - Cuota
        "22": 0,
        # Op. inv. del suj. pasivo (excepto adq. intracom.) - Base
        "23": 0,
        # Op. inv. del suj. pasivo (excepto adq. intracom.) - Cuota
        "24": 0,
        # Modificación bases y cuotas - Base (Compras y ventas)
        "25": -1000,
        # Modificación bases y cuotas - Cuota (Compras y ventas)
        "26": -210,
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
        "39": 1000,
        # Cuotas soportadas en op. int. corrientes - Cuota Intragrupo
        "40": 10,
        # Cuotas soportadas en op. int. bienes de inversión - Base Intragrupo
        "41": 0,  # P_IVAx_BI
        # Cuotas soportadas en op. int. bienes de inversión - Cuota Intragrupo
        "42": 0,  # P_IVAx_BI
        # Rectificación de deducciones - Base Intragrupo
        "43": 0,
        # Rectificación de deducciones - Cuota intragrupo
        "44": 0,
        # Cuotas soportadas en op. int. corrientes - Base Resto
        "45": 2000,
        # Cuotas soportadas en op. int. corrientes - Cuota Resto
        "46": 20,
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
        "57": -1000,
        # Rectificación de deducciones - Cuota Resto
        "58": -10,
        # Compensaciones Rég. especial A. G. y P. - Cuota compras
        "59": 0,
        # Regularización bienes de inversión
        "60": 0,
        # Regularización por aplicación del porcentaje definitivo de prorrata
        "61": 0,
        # Entregas intra. de bienes y servicios - Base ventas
        "71": 0,  # S_IVA0_IC, S_IVA0_SP_I
        # Exportaciones y operaciones asimiladas - Base ventas
        "72": 2000,  # S_IVA0_E + S_IVA0
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
        "61": (100 + 100 - 100 + 100 + 100 - 100) * 0.5
        - (100 + 100 - 100 + 100 + 100 - 100) * 0.1,
        # Entregas intra. de bienes y servicios - Base ventas
        "71": 0,  # S_IVA0_IC, S_IVA0_SP_I
        # Exportaciones y operaciones asimiladas - Base ventas
        "72": 0,  # S_IVA0_E + S_IVA0
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create model
        cls.company.write({"vat": "1234567890", "l10n_es_prorate_enabled": True})
        cls.prorrate_map = cls.env["aeat.map.special.prorrate.year"].create(
            {
                "year": 2023,
                "company_id": cls.company.id,
                "tax_percentage": 10,
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
                "period_type": "01",
                "date_start": "2023-01-01",
                "date_end": "2023-01-31",
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
        cls._invoice_purchase_create(
            "2023-01-01", extra_vals={"partner_id": cls.related_partner.id}
        )
        cls._invoice_purchase_create("2023-01-02")
        purchase = cls._invoice_purchase_create("2023-01-03")
        cls._invoice_refund(purchase, "2023-01-18")
        # Sale invoices
        cls._invoice_sale_create(
            "2023-01-11", extra_vals={"partner_id": cls.related_partner.id}
        )
        cls._invoice_sale_create("2023-01-12")
        sale = cls._invoice_sale_create("2023-01-13")
        cls._invoice_refund(sale, "2023-01-14")

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

    def test_model_322(self):
        _logger.debug("Calculate AEAT 322 1T 2023")
        self.model322.button_calculate()
        self.model322.invalidate_cache()
        # Test default counterpart.
        self.assertEqual(
            self.model322.counterpart_account_id.id, self.accounts["475000"].id
        )
        self.assertEqual(self.model322.state, "calculated")
        # Fill manual fields
        self.model322.write(
            {
                "porcentaje_atribuible_estado": 95,
                "cuota_compensar": 250,
            }
        )
        if self.debug:
            self._print_tax_lines(self.model322.tax_line_ids)
        self._check_tax_lines()
        # Check result
        _logger.debug("Checking results")
        devengado = sum(
            [
                self.taxes_result.get(b, 0.0)
                for b in (
                    "161",
                    "3",
                    "164",
                    "6",
                    "9",
                    "152",
                    "11",
                    "14",
                    "155",
                    "17",
                    "20",
                    "22",
                    "24",
                    "26",
                    "158",
                    "29",
                    "32",
                    "35",
                    "37",
                )
            ]
        )
        deducir = sum(
            [
                self.taxes_result.get(b, 0.0)
                for b in (
                    "40",
                    "42",
                    "44",
                    "46",
                    "48",
                    "50",
                    "52",
                    "54",
                    "56",
                    "58",
                    "59",
                    "60",
                    "61",
                )
            ]
        )
        subtotal = round(devengado - deducir, 3)
        estado = round(subtotal * 0.95, 3)
        result = round(estado - 250, 3)
        self.assertAlmostEqual(self.model322.total_devengado, devengado, 2)
        self.assertAlmostEqual(self.model322.total_deducir, deducir, 2)
        self.assertAlmostEqual(self.model322.casilla_63, subtotal, 2)
        self.assertAlmostEqual(self.model322.atribuible_estado, estado, 2)
        self.assertAlmostEqual(self.model322.cuota_liquidacion, result, 2)
        self.assertAlmostEqual(
            self.model322_4t.tax_line_ids.filtered(
                lambda x: x.field_number == 80
            ).amount,
            0,
        )
        # Export to BOE
        export_to_boe = self.env["l10n.es.aeat.report.export_to_boe"].create(
            {"name": "test_export_to_boe.txt"}
        )
        export_config_xml_ids = [
            "l10n_es_aeat_mod322.aeat_mod322_2023_main_export_config",
        ]
        for xml_id in export_config_xml_ids:
            export_config = self.env.ref(xml_id)
            self.assertTrue(export_to_boe._export_config(self.model322, export_config))
        with self.assertRaises(exceptions.ValidationError):
            self.model322.cuota_compensar = -250
        self.model322.button_post()
        self.assertTrue(self.model322.move_id)
        self.assertEqual(self.model322.move_id.ref, self.model322.name)
        self.assertEqual(
            self.model322.move_id.journal_id,
            self.model322.journal_id,
        )
        self.assertEqual(
            self.model322.move_id.line_ids.mapped("partner_id"),
            self.env.ref("l10n_es_aeat.res_partner_aeat"),
        )
        codes = self.model322.move_id.mapped("line_ids.account_id.code")
        self.assertIn("475000", codes)
        self.assertIn("477000", codes)
        self.assertIn("472000", codes)
        self.model322.button_unpost()
        self.assertFalse(self.model322.move_id)
        self.assertEqual(self.model322.state, "cancelled")
        self.model322.button_recover()
        self.assertEqual(self.model322.state, "draft")
        self.assertEqual(self.model322.calculation_date, False)
        self.model322.button_cancel()
        self.assertEqual(self.model322.state, "cancelled")

    def test_calculate_last_period(self):
        self.model322.period_type = "12"
        self.prorrate_map.compute_prorate()
        self.prorrate_map.close_prorate()
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
