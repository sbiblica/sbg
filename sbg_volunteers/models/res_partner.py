from openerp import models, fields, api, _
from datetime import date, datetime

class sbg_volunteer(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    _description = 'Volunteer'

    volunteer = fields.Boolean('Volunteer')
    church_id = fields.Many2one('sbg.churches', string='Church')
    education_level_id = fields.Many2one('sbg.education.levels', string='Education')
    language_ids = fields.Many2many('sbg.languages', string='Languages')
    professions_talents_ids = fields.Many2many('sbg.professions.talents', string='Professions/talents')
    gender = fields.Selection([('m', 'Male'), ('f', 'Female')], string='Gender')
    civil_status_id = fields.Many2one('sbg.civil.status', string='Civil status')
    birthday = fields.Date('Birthday')
    volunteer_group_id = fields.Many2one('sbg.volunteer.groups', string='Group')
    project_ids = fields.Many2many('sbg.projects', string='Projects interested')
    age = fields.Integer('Age', compute='_age')
    dpi = fields.Char('DPI')
    nationality = fields.Char('Nationality')
    drives = fields.Boolean('Knows how to drive')
    license_type = fields.Char('License type')
    time_disposition = fields.Char('Time disposition')
    experience_ids = fields.One2many('sbg.volunteer.experience', 'volunteer_id', string='Previous volunteer experience')
    birthday_month = fields.Char('Birthday month')

    def _age(self):
        for partner in self:
            if partner.birthday:
                today = date.today()
                birthday = datetime.strptime(partner.birthday, '%Y-%m-%d')
                partner.age = today.year - birthday.year - ((today.month, today.day) < (birthday.month, birthday.day))

    @api.onchange('birthday')
    def onchange_birthday(self):
        month = [_('January'), _('February'), _('March'), _('April'), _('May'), _('June'), _('July'), _('August'), _('September'), _('October'), _('November'), _('December')]
        if self.birthday:
            birthday = datetime.strptime(self.birthday, '%Y-%m-%d')
            self.birthday_month = '{} - {} de {}'.format(str(birthday.month).zfill(2), birthday.day, month[birthday.month])