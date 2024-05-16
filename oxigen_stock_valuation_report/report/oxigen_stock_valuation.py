# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
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
            with mov as (
                select m.id, m.company_id, m.price_unit,
                       (case when m.picking_type_id is not null then t.code
                         when m.inventory_id is not null then 'inventory'
                         when m.scrapped then 'scrap'
                        else null end) as op_type
                from stock_move m
                        left join stock_picking_type t on m.picking_type_id = t.id
            ),
            move_line as (
                select m.company_id, l.id, l.date, l.reference,
                       l.product_id, l.lot_id, l.product_uom_id,
                       l.location_id, l.location_dest_id,
                       l.qty_done, abs(m.price_unit) as price_unit
                from stock_move_line l, mov m, product_product p, product_template t
                where l.move_id = m.id and
                      l.product_id = p.id and
                      p.product_tmpl_id = t.id and
                      t.type = 'product' and
                      l.state = 'done' and
                      l.location_id != l.location_dest_id
            ),
            move_line_stack as (
                select l.company_id, l.date, l.id, l.reference,
                       l.product_id, l.lot_id, l.product_uom_id,
                       l.location_id, 0 as ord_id,
                       -l.qty_done as qty, l.price_unit
                from move_line l
                union all
                select l.company_id, l.date, l.id, l.reference,
                       l.product_id, l.lot_id, product_uom_id,
                       l.location_dest_id as location_id, 1 as ord_id,
                       l.qty_done as qty, l.price_unit
                from move_line l
            ),
            stock_location_alt as (
                select l.id, l.name, (
                case when l.id in (22, 1634) then 'internal' else l.usage end
                ) as usage
                from stock_location l
            ),
            product_cost_current as (
                select distinct t.company_id, p.id, r.value_float as avco
                from ir_property r, ir_model_fields f, ir_model m, product_product p,
                product_template t
                where r.name = 'standard_price' and
                      r.type = 'float' and
                      r.fields_id = f.id and
                      f.ttype = 'float' and
                      f.model_id = m.id and
                      m.model = 'product.product' and
                      f.name = 'standard_price' and
                      r.res_id = 'product.product,' || p.id and
                      p.product_tmpl_id = t.id
            ),
            category_stock_account as (
                select distinct r.company_id, t.id,
                       (regexp_matches
                       (r.value_reference, '^account.account,([0-9]+)')
                       )[1]::numeric as account_id
                from ir_property r, ir_model_fields f, ir_model m, product_category t
                where r.name = 'property_stock_valuation_account_id' and
                      r.type = 'many2one' and
                      r.value_reference like 'account.account,%%' and
                      r.fields_id = f.id and
                      f.ttype = 'many2one' and
                      f.name = 'property_stock_valuation_account_id' and
                      f.model_id = m.id and
                      m.model = 'product.category' and
                      r.res_id = 'product.category,' || t.id
            ),
            product_stock_cost as (
                select s.company_id, s.location_id, s.product_id, s.lot_id, s.product_uom_id,
                       sum(s.qty) as qty
                from move_line_stack s
                where s.date < %s
                group by s.company_id, s.location_id, s.product_id, s.lot_id, s.product_uom_id
                having sum(s.qty) != 0
            )
            select c.company_id, c.location_id, l.name as location_name,
                   c.product_id, pr.default_code as product_code, t.name as product_name,
                   pc.id as category_id, pc.name as category_name,
                   co.id as stock_account_id, co.code as stock_account_code,
                   c.lot_id as tracking_id, o.name as tracking_name, nullif(t.tracking, 'none')
                   as tracking_type,
                   c.product_uom_id as uom_id, u.name as uom_name,
                   c.qty, c.qty*coalesce(p.avco, 0) as cost
            from product_stock_cost c
                    left join stock_production_lot o on c.product_id = o.product_id and
                    coalesce(c.lot_id, -1) = coalesce(o.id, -1)
                    left join product_cost_current p on c.company_id = p.company_id and
                    c.product_id = p.id,
                 stock_location_alt l,
                 product_product pr,
                 product_template t
                    left join category_stock_account cs on t.company_id = cs.company_id and
                    t.categ_id = cs.id
                        left join account_account co on cs.company_id = co.company_id and
                        cs.account_id = co.id,
                 uom_uom u, product_category pc
            where c.location_id = l.id and
                  l.usage = 'internal' and
                  c.product_uom_id = u.id and
                  c.product_id = pr.id and
                  pr.product_tmpl_id = t.id AND
                  t.categ_id = pc.id and
                  c.company_id = %s
            order by c.company_id, c.location_id, c.product_id, c.lot_id
        """
        self.env.cr.execute(
            query,
            (
                tz_naive_local_to_naive_utc(
                    params["date"] + datetime.timedelta(days=1),
                    params["tz"],
                ),
                params["company_id"],
            ),
        )
        headers = [desc[0] for desc in self.env.cr.description]
        data = self.env.cr.fetchall()
        if not data:
            raise UserError(_("Nothing to export."))
        return headers, data

    def generate_xlsx_report(self, workbook, data, partners):
        headers, data = self._prepare_report_oxigen_stock_valuation(data)
        if not self.user_has_groups("account.group_account_manager"):
            raise AccessError(
                _("You do not have the necessary permissions to view this report.")
            )
        report_name = _("Detailed Stock Valuation")
        sheet = workbook.add_worksheet(report_name[:31])
        bold = workbook.add_format({"bold": True})

        sheet.write_row(0, 0, headers, bold)
        for row_num, row_data in enumerate(data, start=1):
            sheet.write_row(row_num, 0, row_data)
