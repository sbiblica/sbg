# -*- coding: utf-8 -*-
from openerp import models, fields, api, _

class sbg_indexes_report_detail(models.Model):
    _name = 'sbg.indexes.report.detail'
    _description = 'Indexes report'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
    date = fields.Date('Date', default=fields.Date.today)
    periodicity = fields.Selection([
        ('d', 'Daily'),
        ('m', 'Monthly'),
        ('w', 'Weekly'),
        ('q', 'Quarterly'),
        ('y', 'Yearly'),
    ], default='m')
    value = fields.Float(string="Value")
    index_report_id = fields.Many2one('sbg.indexes.report', string='Index report')


class sbg_indexes_report(models.Model):
    _name = 'sbg.indexes.report'
    _description = 'Indexes report'

    name = fields.Char(string="Name")
    ref = fields.Char(string="Internal reference")
    date = fields.Date('Date', default=fields.Date.today)
    index_ids = fields.Many2many('sbg.indexes', string='Indexes to generate')
    detail_ids = fields.One2many('sbg.indexes.report.detail', 'index_report_id', string='Indexes')
    state = fields.Selection([('draft', 'Draft'), ('active', 'Active')], default='draft')

    def get_value(self, account_id, period_id):
        balance = 0
        self.env.cr.execute("""
              SELECT COALESCE(SUM(l.debit), 0) - COALESCE(SUM(l.credit), 0) as balance
                FROM account_move_line l
                JOIN account_period p
                ON p.id = l.period_id
                AND p.fiscalyear_id = %(fiscalyear_id)s
                JOIN account_move m
                ON m.id = l.move_id
                AND m.state = 'posted'
                WHERE l.account_id = %(account_id)s
                AND l.date <= %(end_date)s
        """, {'account_id': account_id.id, 'fiscalyear_id': period_id.fiscalyear_id.id, 'end_date': period_id.date_stop})
        for balance_id in self.env.cr.dictfetchall():
            balance += balance_id['balance']
        for child_id in self.env['account.account'].search([('parent_id', '=', account_id.id)]):
            balance += self.get_value(child_id, period_id)
        return balance

    @api.model
    def create(self, vals):
        vals['state'] = 'active'
        return super(sbg_indexes_report, self).create(vals)

    @api.multi
    def generate(self):
        self.env['sbg.indexes.report.detail'].search([('index_report_id', '=', self.id)]).unlink()
        for index_id in self.index_ids:
            period_id = None
            if index_id.periodicity == 'm':
                period_id = self.env['account.period'].search([('date_start', '<=', self.date), ('date_stop', '>=', self.date)])
                if period_id:
                    period_id = period_id[0]
            variable = ''
            variables = []
            for i in range(0, len(index_id.formula)):
                if index_id.formula[i] in ['(', ')', '+', '-', '*', '/', ' ']:
                    if variable != '':
                        variables.append(variable)
                    variable = ''
                else:
                    variable += index_id.formula[i]
            if variable != '':
                variables.append(variable)
            formula = index_id.formula
            for variable in variables:
                value = None
                variable_id = self.env['sbg.variables'].search([('ref', '=', variable)])
                if variable_id:
                    if variable_id.type == 'a' and period_id:
                        value = self.get_value(variable_id.account_id, period_id)
                if value:
                    formula = formula.replace(variable, str(float(value)))
            try:
                value = eval(formula)
            except:
                value = 0

            detail_id = self.env['sbg.indexes.report.detail'].create({
                'name': index_id.name,
                'ref': index_id.ref,
                'date': self.date,
                'periodicity': index_id.periodicity,
                'value': value,
                'index_report_id': self.id
            })
        return True
