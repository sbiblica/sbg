# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date, datetime

class sbg_subs_wizard_statement(models.TransientModel):
    _name = 'sbg.subs.wizard.statement'
    _description = 'View statement wizard'

    def _start_of_year(self):
        now = date(date.today().year, 1, 1)
        return now

    def _end_of_year(self):
        return date.today()

    def _get_partner_subscriptions(self):
        partner_id = self._context.get('partner_id', False)
        ids = self.env['sbg.subscriptions'].search([('partner_id', '=', partner_id)]).distinct_field_get(field='subscription_service_id', value='')
        return self.env["sbg.subscriptions"].search([('id', 'in', ids)])

    def get_date(self, tup):
        return tup.date

    #partner_id = fields.One2many('res.partner', string="Customer", default=_partner)
    start_date = fields.Date(string="Start date", default=_start_of_year)
    end_date = fields.Date(string="End date", default=_end_of_year)
    subscription_ids = fields.Many2many('sbg.subscriptions', string="Subscriptions", default=_get_partner_subscriptions)

    @api.multi
    def action_view_statement(self, context=None):
        partner_id = context.get('partner_id', False)
        detail = self.env['sbg.subs.wizard.stmt.detail']
        detail.search([]).unlink()
        balance = 0
        statement = []

        #
        # Search selected subscriptions and included products
        #
        subscription_ids = []
        product_ids = []
        for subscription in self.subscription_ids:
            subscription_ids.append(subscription.id)
            for product in subscription.subscription_service_id.product_ids:
                if product.id not in product_ids:
                    product_ids.append(product.id)

        #
        # Calculate previous debits amount
        #
        sql_previous_debits = """
            SELECT COALESCE (SUM(value), 0) AS amount
            FROM sbg_subscription_statement
            WHERE subscription_id in %s
            AND date < %s
        """
        self.env.cr.execute(sql_previous_debits, (tuple(subscription_ids), self.start_date,))
        previous_debits = self.env.cr.dictfetchone()
        if previous_debits != None:
            balance += previous_debits['amount']

        #
        # Calculate previous invoices amount
        #
        sql_previous_invoices = """
            SELECT COALESCE (SUM(l.price_unit * l.quantity), 0) AS amount
            FROM account_invoice i
            JOIN account_invoice_line l
            ON l.invoice_id = i.id
            AND l.product_id in %s
            WHERE i.partner_id = %s
            AND i.date_invoice < %s
            AND i.state = 'paid'
        """
        self.env.cr.execute(sql_previous_invoices, (tuple(product_ids), partner_id, self.start_date,))
        previous_invoices = self.env.cr.dictfetchone()
        if previous_invoices != None:
            balance -= previous_invoices['amount']
        initial_balance = balance

        #
        # Calculate debits from statement
        #
        debits = self.env['sbg.subscription.statement'].search([('subscription_id', 'in', subscription_ids),('date', '>=', self.start_date),('date', '<=', self.end_date)])
        for debit in debits:
            balance += debit.value
            statement.append({
                'date': debit.date,
                'name': debit.subscription_id.subscription_service_id.statement_description,
                'debit': debit.value,
                'credit': 0,
                'balance': balance,
            })

        #
        # Insert invoices
        #
        sql_invoices = """
            SELECT i.date_invoice, i.internal_number, l.name, l.price_unit * l.quantity As amount_line
            FROM account_invoice i
            JOIN account_invoice_line l
            ON l.invoice_id = i.id
            AND l.product_id in %s
            WHERE i.partner_id = %s
            AND i.date_invoice between %s and %s
            AND i.state = 'paid'
            ORDER BY i.date_invoice, i.id
        """
        self.env.cr.execute(sql_invoices, (tuple(product_ids), partner_id, self.start_date, self.end_date,))
        for invoice in self.env.cr.dictfetchall():
            statement.append({
                'date': invoice['date_invoice'],
                'name': invoice['internal_number'] + ': ' + invoice['name'],
                'debit': 0,
                'credit': invoice['amount_line'],
                'balance': 0,
            })

        #
        # Sort data and generate report
        #
        statement = sorted(statement, key=lambda tup: tup['date'])
        balance = initial_balance
        for data in statement:
            balance += data['debit'] - data['credit']
            data['balance'] = balance
        statement.insert(0, {
            'date': self.start_date,
            'name': _('Previous balance'),
            'debit': 0,
            'credit': 0,
            'balance': initial_balance
        })
        ids = [detail.create(data) for data in statement]

        return {
            'name': _('Subscription statement:') + ' ' + datetime.strptime(self.start_date, '%Y-%m-%d').strftime('%d/%m/%Y') + ' - ' + datetime.strptime(self.end_date, '%Y-%m-%d').strftime('%d/%m/%Y'),
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'sbg.subs.wizard.stmt.detail',
            'type': 'ir.actions.act_window',
            'context': context,
            'readonly': True,
            'default_order': 'date'
        }
