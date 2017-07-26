# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_volunteer_experience(models.Model):
    _name = 'sbg.volunteer.experience'
    _description = 'Volunteer experience'

    name = fields.Char(string="Place")
    time = fields.Char(string="Time")
    volunteer_id = fields.Many2one('res.partner', 'Volunteer')
