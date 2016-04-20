# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date

class sbg_subs_wizard_stmt_detail(models.TransientModel):
    _name = 'sbg.subs.wizard.stmt.detail'
    _description = 'View statement detail wizard'

    date = fields.Date(string="Date")
    name = fields.Char(string="Description")
    debit = fields.Float(string='Debit', default=0)
    credit = fields.Float(string='Credit', default=0)
    balance = fields.Float(string='Balance', default=0)
