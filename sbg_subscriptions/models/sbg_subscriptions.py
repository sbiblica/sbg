from openerp import models, fields, api, _
from datetime import datetime
from dateutil.relativedelta import relativedelta

class sbg_subscriptions(models.Model):
    _name = 'sbg.subscriptions'
    _description = 'Subscriptions'

    partner_id = fields.Many2one('res.partner', 'Partner', ondelete='set null', select=True)
    subscription_service_id = fields.Many2one('sbg.subscription.services', 'Service', ondelete='set null', select=True)
    name = fields.Char(string="Name", related='subscription_service_id.name')
    fee = fields.Float(string="Fee", related='subscription_service_id.fee')
    start_date = fields.Date(string="Start date")
    statement_ids = fields.One2many('sbg.subscription.statement', 'subscription_id', string='Statement')
    active = fields.Boolean(string="Active", default=True)

    @api.model
    def create(self, values):
        record = super(sbg_subscriptions,self).create(values)
        service_rec = self.env['sbg.subscription.services'].search([('id','=',values['subscription_service_id'])])
        start_date = datetime.strptime(record['start_date'], '%Y-%m-%d')
        if service_rec['start_date'] > record['start_date']:
            start_date = datetime.strptime(service_rec['start_date'], '%Y-%m-%d')
        start_date = datetime(start_date.year, start_date.month, 1)
        end_date = datetime(start_date.year, 12, 31)
        if  end_date < datetime.strptime(service_rec['end_date'], '%Y-%m-%d'):
            end_date = datetime.strptime(service_rec['end_date'], '%Y-%m-%d')
        months = 1
        if service_rec['periodicity'] == 'b':
            months = 2
        elif service_rec['periodicity'] == 'q':
            months = 3
        elif service_rec['periodicity'] == 's':
            months = 6
        elif service_rec['periodicity'] == 'a':
            months = 12
        start_month = start_date.month
        remainder = start_month % months
        if remainder > 0:
            start_month = start_month + (months - start_month % months)
        date = datetime(start_date.year, start_month, 1)
        while date < end_date:
            data = {
                'subscription_id': record['id'],
                'date': date,
                'value': service_rec['fee'],
                'active': True
            }
            self.env['sbg.subscription.statement'].create(data)
            date += relativedelta(months=months)

        return record