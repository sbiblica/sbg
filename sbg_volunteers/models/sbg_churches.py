# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_churches(models.Model):
    _name = 'sbg.churches'
    _description = 'Churches'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
