# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date

class sbg_subs_wizard_stmt_head(models.TransientModel):
    _name = 'sbg.subs.wizard.stmt.head'
    _description = 'View statement header wizard'

    partner_id = fields.Many2one('res.partner', 'Customer')
    name = fields.Char(string="Description")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")
    detail_ids = fields.One2many('sbg.subs.wizard.stmt.detail', 'head_id', string='Detail')
    debits = fields.Float(string='Total debits', default=0)
    credits = fields.Float(string='Total credits', default=0)
    balance = fields.Float(string='Balance', default=0)

    @api.multi
    def render_html(self, context=None):
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('sbg_subscriptions.sbg_subscription_statement_template')
        data = {
            'doc_ids': self._ids,
            'doc_model': report.model,
            'docs': self,
        }
        # return report_obj.render('sbg_subscriptions.sbg_subscription_statement_template', data)
        # return report_obj.get_action(self, 'sbg_subscriptions.sbg_subscription_statement_template', data=data)
        return report_obj.render('sbg_subscriptions.sbg_subscription_statement_template', data)

    @api.multi
    def sbg_print_statement(self):
        return self.env['report'].get_action(self, 'sbg_subscriptions.sbg_subscription_statement_template')

    # @api.multi
    # def sbg_print_statement(self, context=None):
    #     report_obj = self.env['report']
    #     report = report_obj._get_report_from_name('sbg_subscriptions.sbg_subscription_statement_template')
    #     data = {
    #         'doc_ids': self._ids,
    #         'doc_model': report.model,
    #         'docs': self,
    #     }
    #     # return report_obj.render('sbg_subscriptions.sbg_subscription_statement_template', data)
    #     # return report_obj.get_action(self, 'sbg_subscriptions.sbg_subscription_statement_template', data=data)
    #     return report_obj.get_action(self, 'sbg_subscriptions.sbg_subscription_statement_template', data=data)

        #     # if context is None:
    #     #     context = {}
    #     # data = {}
    #     #
    #     # # ids = self.env['sbg.subs.wizard.stmt.head'].search([('id', '=', self.id)])
    #     # # data['ids'] = self._ids
    #     # data['model'] = 'sbg.subs.wizard.stmt.head'
    #     # data['form'] = self.read(['id', 'partner_id',  'name', 'start_date', 'end_date', 'debits', 'credits', 'balance', 'detail_ids'])[0]
    #     # for field in ['id']:
    #     #     if isinstance(data['form'][field], tuple):
    #     #         data['form'][field] = data['form'][field][0]
    #     #
    #     # return self.pool['report'].get_action(self._cr, self._uid, [], 'sbg_subscriptions.sbg_subscription_statement_template', data=data, context=context)
