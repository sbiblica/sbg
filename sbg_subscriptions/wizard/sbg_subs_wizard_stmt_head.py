# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date

class sbg_subs_wizard_stmt_head(models.TransientModel):
    _name = 'sbg.subs.wizard.stmt.head'
    _description = 'View statement header wizard'

    partner_id = fields.Many2one('res.partner', 'Customer')
    name = fields.Char(string="Description")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    detail_ids = fields.One2many('sbg.subs.wizard.stmt.detail', 'head_id', string='Detail')
    debits = fields.Float(string='Total debits', default=0)
    credits = fields.Float(string='Total credits', default=0)
    balance = fields.Float(string='Balance', default=0)
