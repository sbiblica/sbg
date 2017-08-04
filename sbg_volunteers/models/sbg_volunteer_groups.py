# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_volunteer_groups(models.Model):
    _name = 'sbg.volunteer.groups'
    _description = 'Volunteer groups'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
