# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_projects(models.Model):
    _name = 'sbg.projects'
    _description = 'Projects'
    _order = "sequence"

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
    sequence = fields.Integer(string="Sequence")
