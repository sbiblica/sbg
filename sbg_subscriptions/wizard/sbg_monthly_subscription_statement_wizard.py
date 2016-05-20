# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date, datetime
from tempfile import NamedTemporaryFile
from openpyxl import Workbook
from openpyxl.worksheet import ColumnDimension
from openpyxl.styles import Border, Side, Font
import base64
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from calendar import monthrange

class sbg_monthly_subscription_statement_wizard(models.TransientModel):
    _name = 'sbg.monthly.subscription.statement.wizard'
    _description = 'Monthly subscription statement wizard'

    def _get_default_service(self):
        return self.env['sbg.subscription.services'].search([])[0]

    def _start_of_year(self):
        now = date(date.today().year, 1, 1)
        return now

    def _end_of_year(self):
        return date.today()

    def get_date(self, tup):
        return tup.date

    subscription_service_id = fields.Many2one('sbg.subscription.services', 'Subscription service', default=_get_default_service)
    start_date = fields.Date(string="Start date", default=_start_of_year)
    end_date = fields.Date(string="End date", default=_end_of_year)
    name = fields.Char('File Name', readonly=True)
    data = fields.Binary('File', readonly=True)
    state = fields.Selection([('choose', 'choose'),  # choose subscription and period
                              ('get', 'get')],       # get the file
                              default='choose')

    @api.onchange('subscription_service_id')
    def onchange_total_amount(self):
        self.start_date = self.subscription_service_id.start_date
        if self.subscription_service_id.duration_type != 'permanent':
            self.end_date = self.subscription_service_id.end_date

    @api.multi
    def generate_file(self, context=None):
        start_date = parse(self.start_date)
        end_date = parse(self.end_date)

        fileobj = NamedTemporaryFile('w+b')
        xlsfile = fileobj.name
        fileobj.close()

        border_top = Border(top=Side(style='thin'))
        border_bottom = Border(bottom=Side(style='thin'))
        font_bold = Font(bold=True)
        font_h1 = Font(size=18, bold=True)
        font_h2 = Font(size=14, bold=True)

        wb = Workbook()

        ws = wb.active
        ws.title = _('Monthly statement')
        row = 1
        ws.cell(row=row, column=1).value = self.subscription_service_id.name
        ws.cell(row=row, column=1).font = font_h1

        row += 1
        ws.cell(row=row, column=1).value = _('Period')
        ws.cell(row=row, column=1).font = font_h2
        ws.cell(row=row, column=2).value = start_date.strftime('%d/%m/%Y')
        ws.cell(row=row, column=3).value = end_date.strftime('%d/%m/%Y')

        row += 3
        ws.cell(row=row, column=1).value = _('Subscriber')
        ws.cell(row=row, column=1).border = border_bottom

        start_dates = []
        end_dates = []
        col = 2

        date = start_date
        while date < end_date:
            month_end = datetime(date.year, date.month, monthrange(date.year, date.month)[1])
            start_dates.append(date)
            end_dates.append(month_end)
            ws.cell(row=row-1, column=col).value = month_end.strftime('%d/%m/%Y')
            ws.cell(row=row, column=col).value = _('Debits')
            ws.cell(row=row, column=col+1).value = _('Credits')
            ws.cell(row=row, column=col).border = border_bottom
            ws.cell(row=row, column=col+1).border = border_bottom
            col += 2
            date = month_end + relativedelta(days=1)

        #
        # Get debits from subscription statement model
        #
        sql_debits = """
            SELECT r.id, r.display_name, t.date, t.value
            FROM sbg_subscriptions s
            JOIN res_partner r
            ON r.id = s.partner_id
            JOIN sbg_subscription_statement t
            ON t.subscription_id = s.id
            AND t.date BETWEEN %s AND %s
            WHERE s.subscription_service_id = %s
            AND s.start_date <= %s
            ORDER BY r.display_name
        """
        self.env.cr.execute(sql_debits, (self.start_date, self.end_date, self.subscription_service_id.id, self.end_date,))
        last_subscriber = ''
        for subscriber in self.env.cr.dictfetchall():
            if subscriber['display_name'] != last_subscriber:
                last_subscriber = subscriber['display_name']
                row += 1
                ws.cell(row=row, column=1).value = subscriber['display_name']
            date = datetime.strptime(subscriber['date'], '%Y-%m-%d')
            if date in start_dates:
                col = start_dates.index(date) + 2
                ws.cell(row=row, column=(start_dates.index(date) + 1) * 2).value = subscriber['value']

        wb.save(filename=xlsfile)

        spreadsheet_file = open(xlsfile, "rb")
        binary_data = spreadsheet_file.read()
        spreadsheet_file.close()
        out = base64.b64encode(binary_data)
        file_name = _('Monthly subscriptions statement - ') + self.subscription_service_id.name + '.xlsx'

        self.write({
            'state': 'get',
            'name': file_name.encode('utf-8'),
            'data': out
        })
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sbg.monthly.subscription.statement.wizard',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
