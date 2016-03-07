from openerp import models, fields, api, _

class sbg_subscriptions(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Partner'

    sbg_subscription_ids = fields.One2many('sbg.subscriptions', 'partner_id', string='Subscriptions')