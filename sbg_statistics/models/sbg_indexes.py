# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_indexes(models.Model):
    _name = 'sbg.indexes'
    _description = 'Indexes'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
    goal = fields.Float(string="Goal")
    critic_limit = fields.Float(string="Critic limit")
    range = fields.Float(string="Range")
    periodicity = fields.Selection([
        ('d', 'Daily'),
        ('m', 'Monthly'),
        ('w', 'Weekly'),
        ('q', 'Quarterly'),
        ('y', 'Yearly'),
    ], default='m')
    formula = fields.Text('Formula')
    variable_ids = fields.Many2many('sbg.variables', string='Available variables', readonly=True)
