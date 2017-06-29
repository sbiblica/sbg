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

    @api.multi
    def create(self, vals):
        description = self.description
        if 'description' in vals:
            description = vals['description']
        ref = self.ref
        if 'ref' in vals:
            ref = vals['ref']
        vals['name'] = ref.strip() + ' - ' + description.strip()
        return super(sbg_variables, self).create(vals)

    @api.multi
    def write(self, vals):
        description = self.description
        if 'description' in vals:
            description = vals['description']
        ref = self.ref
        if 'ref' in vals:
            ref = vals['ref']
        vals['name'] = ref.strip() + ' - ' + description.strip()
        return super(sbg_variables, self).write(vals)
