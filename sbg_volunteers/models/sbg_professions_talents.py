# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_professions_talents(models.Model):
    _name = 'sbg.professions.talents'
    _description = 'Professions and talents'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
