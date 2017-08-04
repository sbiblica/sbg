# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_volunteer_events(models.Model):
    _name = 'sbg.volunteer.events'
    _description = 'Volunteer events'
    _order = 'start_date'

    name = fields.Char(string="Name")
    description = fields.Text(string="Description")
    start_date = fields.Datetime(string="Start date")
    end_date = fields.Datetime(string="End date")
    responsible_id = fields.Many2one('res.users', 'Responsible')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('open', 'Open'),
        ('finished', 'Finished'),
        ('canceled', 'Canceled')
    ])
    volunteer_ids = fields.Many2many('res.partner', string="Attendees")
