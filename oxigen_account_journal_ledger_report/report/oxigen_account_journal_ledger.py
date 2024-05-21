# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Frank Cespedes <fcespedes@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import datetime

from unidecode import unidecode
from werkzeug.exceptions import BadRequest

from odoo import _, http, models

DATE_FORMAT = "%d-%m-%Y"
DATETIME_FORMAT = "%d-%m-%Y%H:%M:%S"


def _convert_char_to_ansi(char):
    try:
        # Try to encode the character in ANSI
        return char.encode("windows-1252").decode("windows-1252")
    except UnicodeEncodeError:
        # If it fails, use Unidecode for that character
        return unidecode(char)


def _smart_convert_to_ansi(text):
    # Convert each character individually
    return "".join(_convert_char_to_ansi(char) for char in text)


def _smart_convert(field):
    if isinstance(field, datetime.date):
        return field.strftime(DATE_FORMAT)
    elif isinstance(field, datetime.datetime):
        return field.strftime(DATETIME_FORMAT)
    return field


class OxigenAccountJournalLedgerReport(models.AbstractModel):
    _name = "report.report_oxigen_account_journal_ledger_csv"
    _description = "Abstract CSV Oxigen Account Journal Ledger Report"
    _inherit = "report.report_csv.abstract"

    def _prepare_params(self, data):
        fields_conv = {
            "company_ids": tuple,
            "date_from": datetime.date.fromisoformat,
            "date_to": datetime.date.fromisoformat,
        }
        missing_fields = [f for f in fields_conv.keys() if f not in data]
        if missing_fields:
            raise BadRequest(
                _("Missing required fields %s") % ", ".join(missing_fields)
            )
        params = {f: conv(data[f]) for f, conv in fields_conv.items()}
        invalid_companies = set(params["company_ids"]) - set(
            http.request.env.user.company_ids.ids
        )
        if invalid_companies:
            raise BadRequest(_("Wrong Parameters"))
        params["entry"] = f"{params['date_from'].year}/00000"
        return params

    def _prepare_report_oxigen_account_journal_ledger(self, data):
        params = self._prepare_params(data)
        query = """
            with all_previous_entries as (
                select m.company_id,
                       l.account_id, l.partner_id, l.tax_line_id,
                       sum(l.debit) as debit, sum(l.credit) as credit
                from account_move m,
                     account_move_line l
                where m.id = l.move_id
                    and m.state = 'posted'
                    and m.company_id in %(company_ids)s
                    and m."date" < %(date_from)s
                group by m.company_id, l.account_id, l.partner_id, l.tax_line_id
            ),
            open_entries as (
                select l.company_id,
                      -1 AS entry_id, %(entry)s as entry, %(date_from)s::"date" as date,
                      -1 as item_id,
                       l.account_id, l.partner_id, null::integer as tax_line_id,
                       null::text as ref,
                       sum(l.debit) as debit, sum(l.credit) as credit
                from all_previous_entries l, account_account a
                where l.account_id = a.id
                    and substring(a.code, 1, 1) not in ('6', '7') and substring(a.code, 1, 3)
                     not in ('129')
                group by l.company_id, l.account_id, l.partner_id
            ),
            pl_entry as (
                select l.company_id,
                      -2 AS entry_id, %(entry)s as entry, %(date_from)s::"date" as date,
                      -2 as item_id,
                       ra.id as account_id, null::integer as partner_id,
                       null::integer as tax_line_id,
                       null::text as ref,
                       sum(l.debit) as debit, sum(l.credit) as credit
                from all_previous_entries l, account_account a,
                     account_account ra
                where l.account_id = a.id
                    and ra.company_id = l.company_id
                    and ra.code = '129000000'
                    and (substring(a.code, 1, 1) in ('6', '7') or substring(a.code, 1, 3)
                     in ('129'))
                group by l.company_id, ra.id
            ),
            period_entries as (
                select m.company_id,
                       m.id AS entry_id, m."name" as entry, m."date",
                       l.id as item_id,
                       l.account_id, l.partner_id, l.tax_line_id,
                       l.ref,
                       l.debit, l.credit
                from account_move m,
                     account_move_line l
                where m.id = l.move_id
                    and m.state = 'posted'
                    and m.company_id in %(company_ids)s
                    and m."date" between %(date_from)s and %(date_to)s
            ),
            all_entries as (
                select e.company_id, '0-Opening' as type,
                       e.entry_id, e.entry, e.date,
                       e.item_id,
                       e.account_id, e.partner_id, e.tax_line_id,
                       e.ref,
                       (case when e.debit - e.credit >= 0 then round(e.debit - e.credit, 2)
                        else 0 end) as debit,
                       (case when e.debit - e.credit < 0 then round(e.credit - e.debit, 2)
                        else 0 end) as credit
                from open_entries e
                where round(e.debit, 2) != round(e.credit, 2)
                union all
                select e.company_id, '1-P&L' AS type,
                       e.entry_id, e.entry, e.date,
                       e.item_id,
                       e.account_id, e.partner_id, e.tax_line_id,
                       e.ref,
                       (case when e.debit - e.credit >= 0 then round(e.debit - e.credit, 2)
                        else 0 end) as debit,
                       (case when e.debit - e.credit < 0 then round(e.credit - e.debit, 2)
                        else 0 end) as credit
                from pl_entry e
                where round(e.debit, 2) != round(e.credit, 2)
                union all
                select e.company_id, '2-Item' as type,
                       e.entry_id, e.entry, e.date,
                       e.item_id,
                       e.account_id, e.partner_id, e.tax_line_id,
                       e.ref,
                       e.debit, e.credit
                from period_entries e
            ),
            partner_all_entries as (
                select l.company_id, l.type,
                       l.entry_id, l.entry, l."date",
                       l.item_id,
                       l.account_id,
                       (case when substring(a.code, 1, 3) in (
                                '400', '410', '411', '430', '433', '465', '407', '413'
                                ) then l.partner_id
                             when substring(a.code, 1, 4) in (
                                '4310', '4312') then l.partner_id
                        else null end) as partner_id,
                       l.tax_line_id,
                       l."ref",
                       l.debit, l.credit
                from all_entries l, account_account a
                where l.account_id = a.id
            ),
            grouped_all_entries as (
                 select l.company_id, l.type,
                       l.entry_id, l.entry, l."date",
                       l.item_id,
                       l.account_id,
                       l.partner_id,
                       l.tax_line_id,
                       l."ref",
                       sum(l.debit) as debit, sum(l.credit) as credit
                 from partner_all_entries l
                 group by l.company_id, l.type, l.entry_id, l.entry, l."date",
                          l.item_id, l.account_id, l.partner_id, l.tax_line_id, l."ref"
            )
            select l.company_id, l.type,
                   l.entry_id, l.entry, l."date",
                   l.item_id,
                   a.code as account,
                   a."name" as account_name,
                   l.partner_id,
                   (case when l.partner_id is not null then
                        substring(a.code, 1, length(a.code)-length(l.partner_id::varchar))
                         || l.partner_id::varchar
                    else a.code
                    end) as account_partner,
                   (case when l.partner_id is not null then
                        p."name"
                    else a."name"
                    end) as account_name_partner,
                   p."name" as partner,
                   p.vat as partner_vat,
                   replace(replace(l."ref", CHR(13), ' '), CHR(10), ' ') as "ref",
                   l.debit, l.credit
            from grouped_all_entries l
                    left join res_partner p on l.partner_id = p.id
                    left join account_tax t on l.tax_line_id = t.id,
                 account_account a
            where l.account_id = a.id
            order by l.company_id, l.type, l.entry, l.item_id, a.code
        """
        self.env.cr.execute(
            query,
            {
                "company_ids": params["company_ids"],
                "date_from": params["date_from"],
                "date_to": params["date_to"],
                "entry": params["entry"],
            },
        )
        headers = [desc[0] for desc in self.env.cr.description]
        result = self.env.cr.fetchall()
        if not result:
            raise BadRequest(_("Nothing to export."))
        data = []
        for row in result:
            data.append(dict(zip(headers, row)))
        return headers, data

    def generate_csv_report(self, file, data, objs):
        headers, content = self._prepare_report_oxigen_account_journal_ledger(data)
        if not self.user_has_groups("account.group_account_manager"):
            raise BadRequest(
                _("You do not have the necessary permissions to view this report.")
            )
        file.fieldnames = headers
        file.writeheader()
        for row in content:
            row = {k: _smart_convert(v) for k, v in row.items()}
            file.writerow(row)

    def create_csv_report(self, docids, data):
        csv_content, file_type = super().create_csv_report(docids, data)
        try:
            encoded_content = csv_content.encode("windows-1252")
        except UnicodeEncodeError:
            encoded_content = _smart_convert_to_ansi(csv_content)
        return encoded_content, file_type
