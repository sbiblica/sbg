# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from datetime import date, datetime

class sbg_subs_wizard_statement(models.TransientModel):
    _name = 'sbg.subs.wizard.statement'
    _description = 'View statement wizard'

    def _get_partner(self):
        partner_id = self._context.get('partner_id', False)
        return self._context.get('partner_id', False)

    def _start_of_year(self):
        now = date(date.today().year, 1, 1)
        return now

    def _end_of_year(self):
        return date.today()

    def _get_partner_subscriptions(self):
        partner_id = self._context.get('partner_id', False)
        return self.env["sbg.subscriptions"].search([('id', 'in', self.env['sbg.subscriptions'].search([('partner_id', '=', partner_id)])._ids)])

    def get_date(self, tup):
        return tup.date

    partner_id = fields.Many2one('res.partner', 'Customer', default=_get_partner)
    start_date = fields.Date(string="Start date", default=_start_of_year)
    end_date = fields.Date(string="End date", default=_end_of_year)
    subscription_ids = fields.Many2many('sbg.subscriptions', string="Subscriptions", default=_get_partner_subscriptions)

    @api.multi
    def action_view_statement(self, context=None):
        partner_id = context.get('partner_id', False)
        head = self.env['sbg.subs.wizard.stmt.head']
        detail = self.env['sbg.subs.wizard.stmt.detail']
        head.search([]).unlink()
        detail.search([]).unlink()
        total_debits = 0
        total_credits = 0
        balance = 0
        statement = []

        head_id = head.create({
            'partner_id': partner_id,
            'name': _('Subscription statement'),
            'start_date': self.start_date,
            'end_date': self.end_date,
        })

        #
        # Search selected subscriptions and included products
        #
        subscription_ids = []
        product_ids = []
        start_dates = []
        for subscription in self.subscription_ids:
            subscription_ids.append(subscription.id)
            start_dates.append(subscription.start_date)
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
            AND i.state = 'paid'
            AND i.date_invoice < %s
            AND i.date_invoice >= %s
        """
        first_date = None
        for initial_date in start_dates:
            if first_date == None:
                first_date = initial_date
            elif initial_date < first_date:
                first_date = initial_date
        if first_date == None:
            first_date = self.start_date
        self.env.cr.execute(sql_previous_invoices, (tuple(product_ids), partner_id, self.start_date, first_date,))
        previous_invoices = self.env.cr.dictfetchone()
        if previous_invoices != None:
            balance -= previous_invoices['amount']
        initial_balance = balance

        #
        # Calculate debits from statement
        #
        debits = self.env['sbg.subscription.statement'].search([('subscription_id', 'in', subscription_ids),('date', '>=', self.start_date),('date', '<=', self.end_date)])
        for debit in debits:
            total_debits += debit.value
            balance += debit.value
            statement.append({
                'head_id': head_id.id,
                'date': debit.date,
                'name': debit.subscription_id.subscription_service_id.statement_description,
                'debit': debit.value,
                'credit': 0,
                'balance': balance,
                'type': 'debit',
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
            total_credits += invoice['amount_line']
            statement.append({
                'head_id': head_id.id,
                'date': invoice['date_invoice'],
                'name': invoice['internal_number'] + ': ' + invoice['name'],
                'debit': 0,
                'credit': invoice['amount_line'],
                'balance': 0,
                'type': 'credit',
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
            'head_id': head_id.id,
            'date': self.start_date,
            'name': _('Initial balance'),
            'debit': 0,
            'credit': 0,
            'balance': initial_balance,
            'type': 'total',
        })
        statement.append({
            'head_id': head_id.id,
            'date': self.end_date,
            'name': _('Total'),
            'debit': total_debits,
            'credit': total_credits,
            'balance': balance,
            'type': 'total',
        })
        ids = [detail.create(data) for data in statement]
        head_id.write({
            'debits': total_debits,
            'credits': total_credits,
            'balance': balance,
        })

        return {
            'name': _('Subscription statement:'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'sbg.subs.wizard.stmt.head',
            'res_id': head_id.id,
            'type': 'ir.actions.act_window',
            'context': context,
            'readonly': True
        }
