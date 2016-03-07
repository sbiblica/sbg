from openerp import models, fields, api, _

class sbg_subscription_statement(models.Model):
    _name = 'sbg.subscription.statement'
    _description = 'Subscription statement'

    subscription_id = fields.Many2one('sbg.subscriptions', 'Subscription')
    date = fields.Date(string="Date", default=fields.Date.today)
    value = fields.Float(string='Value', default=0)
    active = fields.Boolean(string="Active", default=True)