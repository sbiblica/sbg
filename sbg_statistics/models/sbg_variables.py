# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_variables(models.Model):
    _name = 'sbg.variables'
    _description = 'Financial variables'

    name = fields.Char(string="Name")
    description = fields.Char(string="Description")
    ref = fields.Char(string="Internal reference")
    type = fields.Selection([
        ('a', 'Account'),
        ('d', 'Date'),
    ], default="a")
    account_id = fields.Many2one('account.account', string="Account")

    @api.model
    def create(self, vals):
        vals['name'] = '{} - {}'.format(vals.get('ref', self.ref), vals.get('description', self.description))
        return super(sbg_variables, self).create(vals)

    @api.multi
    def write(self, vals):
        vals['name'] = '{} - {}'.format(vals.get('ref', self.ref), vals.get('description', self.description))
        return super(sbg_variables, self).write(vals)
