from openerp import models, fields, api, _
from datetime import date

class sbg_subs_wizard_statement(models.TransientModel):
    _name = 'sbg.subs.wizard.statement'
    _description = 'View statement wizard'

    def _start_of_year(self):
        now = date(date.today().year, 1, 1)
        return now

    def _end_of_year(self):
        return date(date.today().year, 12, 31)

    #partner_id = fields.One2many('res.partner', string="Customer", default=_partner)
    start_date = fields.Date(string="Start date", default=_start_of_year)
    end_date = fields.Date(string="End date", default=_end_of_year)
    subscription_ids = fields.Many2many('sbg.subscriptions', string="Subscriptions")

    @api.multi
    def action_view_statement(self, context=None):
        partner_id = context.get('partner_id', False)
        detail = self.env['sbg.subs.wizard.stmt.detail']
        detail.search([]).unlink();
        subscriptions = self.env['sbg.subscriptions'].search([('partner_id', '=', partner_id)])
        subscription_ids = []
        for subscription in subscriptions:
            subscription_ids.append(subscription.id)
        debits = self.env['sbg.subscription.statement'].search([('subscription_id', 'in', subscription_ids),('date', '>=', self.start_date),('date', '<=', self.end_date)])
        balance = 0
        for debit in debits:
            balance += debit.value
            data = {
                'date': debit.date,
                'name': debit.subscription_id.name,
                'debit': debit.value,
                'credit': 0,
                'balance': balance,
            }
            detail.create(data)
        return {
            'name': _('Statement'),
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'sbg.subs.wizard.stmt.detail',
            'type': 'ir.actions.act_window',
            'context': context,
            'readonly': True
        }
