# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_education_levels(models.Model):
    _name = 'sbg.education.levels'
    _description = 'Education levels'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
