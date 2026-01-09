# Copyright NuoBiT Solutions - Frank Cespedes <fcespedes@nuobit.com>
# Copyright 2026 NuoBiT Solutions - Deniz Gallo <dgallo@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from odoo import _, models
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.safe_eval import pytz


def tz_naive_local_to_naive_utc(dt, tz):
    if isinstance(dt, datetime.date):
        dt = datetime.datetime.combine(dt, datetime.time())
    datetime_local = pytz.timezone(tz).localize(dt)
    datetime_utc = datetime_local.astimezone(pytz.utc)
    datetime_naive_utc = datetime_utc.replace(tzinfo=None)
    return datetime_naive_utc


class OxigenStockValuationXslx(models.AbstractModel):
    _name = "report.report_oxigen_stock_valuation_xlsx"
    _description = "Abstract XLSX Oxigen Stock Valuation Report"
    _inherit = "report.report_xlsx.abstract"

    def _prepare_params(self, data):
        fields_conv = {
            "company_id": int,
            "date": datetime.date.fromisoformat,
            "tz": str,
        }
        missing_fields = [f for f in fields_conv.keys() if f not in data]
        if missing_fields:
            raise ValidationError(
                _("Missing required fields: %s") % ", ".join(missing_fields)
            )
        params = {f: conv(data[f]) for f, conv in fields_conv.items()}
        return params

    def _prepare_report_oxigen_stock_valuation(self, data):
        params = self._prepare_params(data)
        query = """
            with account_account_company as (
                select a.id,
                r.res_company_id as company_id,
                a.code_store->>r.res_company_id::text as code,
                a.name->>'en_US' as name
                from account_account a
                    join account_account_res_company_rel r
                    on a.id = r.account_account_id
            ),
            mov as (
                SELECT
				    m.id,
				    m.company_id, m.price_unit,
				    case
				        when m.picking_type_id is not null then pt.code
				        when src.usage = 'inventory'
				          OR dest.usage = 'inventory' then 'inventory'
				        when m.scrapped then 'scrap'
				        else null
				    END AS op_type
				FROM stock_move m
				LEFT JOIN stock_picking_type pt
				    ON m.picking_type_id = pt.id
				LEFT JOIN stock_location src
				    ON m.location_id = src.id
				LEFT JOIN stock_location dest
				    ON m.location_dest_id = dest.id
            ),
            move_line as (
                select m.company_id, l.id, l.date, l.reference,
                       l.product_id, l.lot_id, l.product_uom_id,
                       l.location_id, l.location_dest_id,
                       l.quantity, abs(m.price_unit) as price_unit
                from stock_move_line l, mov m, product_product p, product_template t
                where l.move_id = m.id and
                      l.product_id = p.id and
                      p.product_tmpl_id = t.id and
                      t.type = 'consu' and
                      t.is_storable = true and
                      l.state = 'done' and
                      l.location_id != l.location_dest_id
            ),
            move_line_stack as (
                select l.company_id, l.date, l.id, l.reference,
                       l.product_id, l.lot_id, l.product_uom_id,
                       l.location_id, 0 as ord_id,
                       -l.quantity as qty, l.price_unit
                from move_line l
                union all
                select l.company_id, l.date, l.id, l.reference,
                       l.product_id, l.lot_id, product_uom_id,
                       l.location_dest_id as location_id, 1 as ord_id,
                       l.quantity as qty, l.price_unit
                from move_line l
            ),
            stock_location_alt as (
                select l.id, l.name, (
                case when l.id in (22, 1634) then 'internal' else l.usage end
                ) as usage
                from stock_location l
            ),
            product_cost_current as (
                SELECT
				    t.company_id,
				    p.id,
				    (p.standard_price->>t.company_id::text)::float as avco
				FROM product_product p
				JOIN product_template t
				    ON p.product_tmpl_id = t.id
            ),
            category_stock_account as (
                select
                    a.company_id,
                    c.id,
                    (c.property_stock_valuation_account_id
                        ->>a.company_id::text
                    )::int AS account_id
                FROM product_category c
                JOIN account_account_company a
                    ON (c.property_stock_valuation_account_id
                        ->>a.company_id::text
                    )::int = a.id
            ),
            product_stock_cost as (
                select s.company_id, s.location_id,
                s.product_id, s.lot_id, s.product_uom_id,
                       sum(s.qty) as qty
                from move_line_stack s
                where s.date < %(date)s
                group by s.company_id, s.location_id,
                s.product_id, s.lot_id, s.product_uom_id
                having sum(s.qty) != 0
            )
            select c.company_id, c.location_id, l.name as location_name,
                   c.product_id, pr.default_code
                   as product_code, t.name->>%(lang)s as product_name,
                   pc.id as category_id, pc.name as category_name,
                   co.id as stock_account_id, co.code as stock_account_code,
                   c.lot_id as tracking_id, o.name as tracking_name, nullif(
                    t.tracking, 'none'
                   )
                   as tracking_type,
                   c.product_uom_id as uom_id, u.name->>%(lang)s as uom_name,
                   c.qty, c.qty*coalesce(p.avco, 0) as cost
            from product_stock_cost c
                    left join stock_lot o on c.product_id = o.product_id and
                    coalesce(c.lot_id, -1) = coalesce(o.id, -1)
                    left join product_cost_current p on c.company_id = p.company_id and
                    c.product_id = p.id,
                 stock_location_alt l,
                 product_product pr,
                 product_template t
                    left join category_stock_account cs on t.company_id = cs.company_id
                    and t.categ_id = cs.id
                        left join account_account_company co
                        on cs.company_id = co.company_id
                        and cs.account_id = co.id,
                 uom_uom u, product_category pc
            where c.location_id = l.id and
                  l.usage = 'internal' and
                  c.product_uom_id = u.id and
                  c.product_id = pr.id and
                  pr.product_tmpl_id = t.id AND
                  t.categ_id = pc.id and
                  c.company_id = %(company)s
            order by c.company_id, c.location_id, c.product_id, c.lot_id
        """
        self.env.cr.execute(
            query,
            {
                "date": tz_naive_local_to_naive_utc(
                    params["date"] + datetime.timedelta(days=1),
                    params["tz"],
                ),
                "lang": self.env.lang,
                "company": params["company_id"],
            },
        )
        headers = [desc[0] for desc in self.env.cr.description]
        data = self.env.cr.fetchall()
        if not data:
            raise UserError(_("Nothing to export."))
        return headers, data

    def generate_xlsx_report(self, workbook, data, partners):
        headers, data = self._prepare_report_oxigen_stock_valuation(data)
        if not self.env.user.has_group("account.group_account_manager"):
            raise AccessError(
                _("You do not have the necessary permissions to view this report.")
            )
        report_name = _("Detailed Stock Valuation")
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({"bold": True})

        sheet.write_row(0, 0, headers, bold)
        for row_num, row_data in enumerate(data, start=1):
            sheet.write_row(row_num, 0, row_data)
