# -*- coding: utf-8 -*-

#######################################################################################
#
# Filename:     unapplied_payments.py
# Author:       Ursa Information Systems
# Description:  Create sql views consisting of unreconciled customer/supplier 
#               deposits. Unapplied customer deposits are used in customer aging view
#
#######################################################################################

from openerp.osv import osv, fields
from openerp import tools

class account_move_line(osv.osv):

    _inherit = 'account.move.line'
    
    _columns = {
        'open_ar': fields.boolean('Open AR Entry'),
        'open_ap': fields.boolean('Open AP Entry'),
        'open_invoice': fields.boolean('Open Invoice Balance Entry')
        }

class customer_unapplied(osv.osv):
  
    _name = 'account.voucher.customer.unapplied'
    _auto = False

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner', readonly=True),
        'partner_name': fields.text('Name', readonly=True),
        'salesman': fields.many2one('res.users', u'Sales Rep', readonly=True),
        'avg_days_overdue': fields.integer(u'Avg Days Overdue', readonly=True),
        'oldest_invoice_date': fields.date(u'Invoice Date', readonly=True),
        'date_due': fields.date(u'Due Date',readonly=True),
        'total': fields.float(u'Total', readonly=True),
        'unapp_cash': fields.float(u'Unapplied Cash', readonly=True),
        'not_due': fields.float(u'Not Due Yet', readonly=True),
        'current': fields.float(u'Current', readonly=True),
        'days_due_01to30': fields.float(u'1/30', readonly=True),
        'days_due_31to60': fields.float(u'31/60', readonly=True),
        'days_due_61to90': fields.float(u'61/90', readonly=True),
        'days_due_91to120': fields.float(u'91/120', readonly=True),
        'days_due_121togr': fields.float(u'+121', readonly=True),
        'max_days_overdue': fields.integer(u'Days Overdue', readonly=True),
        'invoice_ref': fields.char('Reference',size=128),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True), 
        'comment': fields.text('Notes', readonly=True),
        'unapp_credits': fields.float(u'Unapplied Credits', readonly=True),
   }

    _order = "partner_name"

    def init(self, cr):

        query="""
               SELECT cast(100000000000 + av.id as bigint) as id,rp.id as partner_id, rp.name as partner_name, days_due as avg_days_overdue, 
                      av.date as oldest_invoice_date, av.date_due as "date_due",
                      (select -1 * (sum(credit) - sum(debit)) from account_move_line where move_id = av.move_id and reconcile_id is NULL
                           and account_id in (select id from account_account where type = 'receivable')) as total,  
                      (select -1 * (sum(credit) - sum(debit)) from account_move_line where move_id = av.move_id and reconcile_id is NULL
                           and account_id in (select id from account_account where type = 'receivable')) AS "unapp_cash",  
                      0 AS "days_due_01to30",                           
                      CASE WHEN (days_due BETWEEN 31 AND 60) THEN 
                           (select -1 * (sum(credit) - sum(debit)) from account_move_line where move_id = av.move_id and reconcile_id is NULL
                           and account_id in (select id from account_account where type = 'receivable')) END  AS "days_due_31to60",
                      CASE WHEN (days_due BETWEEN 61 AND 90) THEN 
                           (select -1 * (sum(credit) - sum(debit)) from account_move_line where move_id = av.move_id and reconcile_id is NULL
                           and account_id in (select id from account_account where type = 'receivable')) END  AS "days_due_61to90",
                      CASE WHEN (days_due BETWEEN 91 AND 120) THEN 
                           (select -1 * (sum(credit) - sum(debit)) from account_move_line where move_id = av.move_id and reconcile_id is NULL
                           and account_id in (select id from account_account where type = 'receivable')) END AS "days_due_91to120",
                      CASE WHEN (days_due >= 121) THEN 
                           (select -1 * (sum(credit) - sum(debit)) from account_move_line where move_id = av.move_id and reconcile_id is NULL
                           and account_id in (select id from account_account where type = 'receivable')) END  AS "days_due_121togr",
                      CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                      CASE WHEN (days_due < 31) THEN 
                           (select -1 * (sum(credit) - sum(debit)) from account_move_line where move_id = av.move_id and reconcile_id is NULL
                           and account_id in (select id from account_account where type = 'receivable')) END  AS "not_due",
                        0 AS "current",
                           av.number as invoice_ref, -999 as "invoice_id", null as comment, 0 as salesman,
                        0 AS "unapp_credits"
                        
               FROM account_voucher av,res_partner rp, account_move_line aml
               INNER JOIN
                  ( SELECT id, current_date - aml2.date AS days_due  FROM account_move_line aml2 ) DaysDue
                ON DaysDue.id = aml.id

               WHERE         
                    av.partner_id = rp.id
                    and av.move_id = aml.move_id
                    and av.state = 'posted'
                    and aml.reconcile_id is null 
                    and aml.reconcile_partial_id is null
                    and aml.account_id in (select id from account_account where type = 'receivable')
                    and aml.credit > 0

        """

        tools.drop_view_if_exists(cr, '%s'%(self._name.replace('.', '_')))
        cr.execute("""
                      CREATE OR REPLACE VIEW %s AS ( %s) 
        """%(self._name.replace('.', '_'), query) ) 