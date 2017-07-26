# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_civil_status(models.Model):
    _name = 'sbg.civil.status'
    _description = 'Civil status'

    name = fields.Char(string="Name")
