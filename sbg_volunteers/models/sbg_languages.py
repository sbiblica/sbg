# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_languages(models.Model):
    _name = 'sbg.languages'
    _description = 'Languages'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
