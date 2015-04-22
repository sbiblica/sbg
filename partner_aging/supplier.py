# -*- coding: utf-8 -*-

######################################################################
#
#  Note: Program metadata is available in /__init__.py
#
######################################################################

from openerp.osv import fields, osv
from openerp import tools

class partner_aging_supplier(osv.osv):
  
    _name = 'partner.aging.supplier'
    _auto = False

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        if 'max_days_overdue' in fields:
            fields.remove('max_days_overdue')
        return super(partner_aging_supplier, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby)
    
    def invopen(self, cr, uid, ids, context=None):
        """
        @author       Ursa Information Systems
        @description  Create link to view each listed invoice
        """
        models = self.pool.get('ir.model.data')
        view = models.get_object_reference(cr, uid, 'account', 'invoice_form')
        view_id = view and view[1] or False
        
        if not context: 
            context = {} 
        active_id  = context.get('active_id') 
        inv_id = self.browse(cr, uid, ids[0]).invoice_id.id 
   
        print active_id
        print inv_id

        
        return {
            'name': ('Supplier Invoices'),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_model': 'account.invoice',
            'context': "{'type':'in_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': inv_id,
        }

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner',readonly=True),
        'partner_name': fields.text('Name',readonly=True),
        'max_days_overdue': fields.integer(u'Days Outstanding',readonly=True),
        'avg_days_overdue': fields.integer(u'Avg Days Overdue',readonly=True),
        'date': fields.date(u'Date',readonly=True),
        'date_due': fields.date(u'Due Date',readonly=True),
        'total': fields.float(u'Total',readonly=True),
        'not_due': fields.float(u'Not Due Yet', readonly=True),
        'current': fields.float(u'Current', readonly=True),
        'days_due_01to30': fields.float(u'1/30', readonly=True),
        'days_due_31to60': fields.float(u'31/60',readonly=True),
        'days_due_61to90': fields.float(u'61/90',readonly=True),
        'days_due_91to120': fields.float(u'91/120',readonly=True),
        'days_due_121togr': fields.float(u'+121',readonly=True),
        'invoice_ref': fields.char('Their Invoice',size=25,readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'comment': fields.text('Notes',readonly=True),
        'unapp_credits': fields.float(u'Unapplied Credits', readonly=True),
        'unapp_cash': fields.float(u'Unapplied Cash', readonly=True),
     }
     
    _order = 'partner_name'

    def init(self, cr):
        """
        @author        Ursa Information Systems
        @description   Populate supplier aging view with up to date data on load
        @modified      2015-03-18
        """

        query = """
                select aml.id, partner_id, NULL AS partner_name, days_due AS avg_days_overdue, NULL as date, date as date_due,                 
                
                CASE WHEN reconcile_partial_id is not NULL THEN credit-
                    (select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit-debit) END AS TOTAL, 0 AS unapp_cash,
                
                CASE WHEN (days_due BETWEEN 31 and 60) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN credit-(select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit-debit) END
                ELSE 0 END AS days_due_31to60, 
                
                CASE WHEN (days_due BETWEEN 61 and 90) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN credit-(select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit-debit) END
                ELSE 0 END AS days_due_61to90,
                
                CASE WHEN (days_due BETWEEN 91 and 120) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN credit-(select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit-debit) END
                ELSE 0 END AS days_due_91to120,
                
                CASE WHEN (days_due >= 121) THEN                     
                    CASE WHEN reconcile_partial_id is not NULL THEN credit-(select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit-debit) END
                ELSE 0 END AS days_due_121togr,
                
                CASE WHEN days_due < 1 THEN
                    CASE WHEN reconcile_partial_id is not NULL THEN credit-(select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit-debit) END
                ELSE 0 END AS not_due,
                
                0 AS "current",                
                CASE WHEN (days_due BETWEEN 1 and 30) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN credit-(select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit-debit) END
                ELSE 0 END AS days_due_01to30,
                
                CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                
                name AS invoice_ref, -14156 as invoice_id, NULL AS comment, 
                
                CASE WHEN reconcile_partial_id is not NULL THEN credit-
                        (select sum(l.debit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (credit -debit)
                END AS unapp_credits

                   from account_move_line aml 
                   
                INNER JOIN
                  ( SELECT aml2.id, (current_date - aml2.date) AS days_due  FROM account_move_line aml2 ) DaysDue
                ON DaysDue.id = aml.id
                
                where 
                    open_ap = 't'
                    AND reconcile_id is NULL 
                    AND account_id in (select id from account_account where type = 'payable')
                    UNION 
                select id, partner_id, partner_name, avg_days_overdue, oldest_invoice_date as date, date_due, total, unapp_cash,
                       days_due_31to60, days_due_61to90, days_due_91to120, days_due_121togr, not_due, current, days_due_01to30, max_days_overdue, invoice_ref, invoice_id, comment, unapp_credits
                       from account_voucher_supplier_unapplied UNION                    
                select id, partner_id, partner_name, avg_days_overdue, NULL as date, date_due, total, unapp_cash,
                       days_due_31to60, days_due_61to90, days_due_91to120, days_due_121togr, not_due, current, days_due_01to30, max_days_overdue, invoice_ref, invoice_id, comment, unapp_credits
                       from (            
                SELECT l.id as id, l.partner_id as partner_id, res_partner.name as "partner_name",
                    CASE WHEN ai.id is not null THEN ai.date_due ElSE l.date END as "date_due",
                    days_due as "avg_days_overdue", 
                    l.date as "date",
                    CASE WHEN ai.type = 'in_refund' AND ai.id is not null THEN -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) ELSE ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed)
                         END as "total",
                    CASE WHEN (days_due BETWEEN 31 AND  60) and ai.id is not null THEN
                             CASE WHEN ai.type = 'in_refund' THEN -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) ELSE ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) END 
                         WHEN (days_due BETWEEN 31 and 60) and ai.id is null THEN l.credit - l.debit 
                         ELSE 0 END  AS "days_due_31to60",
                    CASE WHEN (days_due BETWEEN 61 AND  90) and ai.id is not null THEN 
                             CASE WHEN ai.type = 'in_refund' THEN -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) ELSE ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) END 
                         WHEN (days_due BETWEEN 61 and 90) and ai.id is null THEN l.credit - l.debit 
                         ELSE 0 END  AS "days_due_61to90",
                    CASE WHEN (days_due BETWEEN 91 AND 120) and ai.id is not null THEN 
                             CASE WHEN ai.type = 'in_refund' THEN -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) ELSE ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) END 
                         WHEN (days_due BETWEEN 91 and 120) and ai.id is null THEN l.credit - l.debit 
                         ELSE 0 END  AS "days_due_91to120",
                    CASE WHEN days_due >=121 and ai.id is not null THEN 
                             CASE WHEN ai.type = 'in_refund' THEN -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) ELSE ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) END 
                         WHEN days_due >=121 and ai.id is null THEN l.debit-l.credit 
                         ELSE 0 END AS "days_due_121togr",
                         
                    CASE WHEN (days_due < 1) and ai.id is not null THEN 
                             CASE WHEN ai.type = 'in_refund' then -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) ELSE ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) END 
                         WHEN (days_due < 1) and ai.id is null THEN l.credit - l.debit 
                         ELSE 0 END  AS "not_due",
                    0 AS "current",                                
                    CASE WHEN (days_due BETWEEN 1 and 30) and ai.id is not null THEN 
                             CASE WHEN ai.type = 'in_refund' then -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) ELSE ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) END 
                         WHEN (days_due BETWEEN 1 and 30) and ai.id is null THEN l.credit - l.debit 
                         ELSE 0 END  AS "days_due_01to30",
                         
                    CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                    0 AS "unapp_cash",
                    CASE WHEN ai.type = 'in_refund' THEN -1*ai.residual*ABS((l.debit - l.credit)/ai.amount_untaxed) END AS "unapp_credits",
                    ai.supplier_invoice_number as "invoice_ref",
                    ai.id as "invoice_id", ai.comment
                   
                    FROM account_move_line as l     
                INNER JOIN         
                  (     
                   SELECT lt.id, 
                   CASE WHEN inv.date_due is null then 0
                   WHEN inv.id is not null THEN current_date - inv.date_due 
                   ELSE current_date - lt.date END AS days_due            
                   FROM account_move_line lt LEFT JOIN account_invoice inv on lt.move_id = inv.move_id   
                ) DaysDue       
                ON DaysDue.id = l.id               
                                  
                INNER JOIN account_account
                   ON account_account.id = l.account_id
                INNER JOIN res_company
                   ON account_account.company_id = res_company.id
                INNER JOIN account_move
                   ON account_move.id = l.move_id
                LEFT JOIN account_invoice as ai
                   ON ai.move_id = l.move_id
                INNER JOIN res_partner
                   ON res_partner.id = l.partner_id
                WHERE account_account.active
                  AND (account_account.type IN ('payable'))     
                  AND account_move.state = 'posted'
                  AND l.reconcile_id IS NULL
                  AND ai.state <> 'paid'
                ) sq
              """
            
        tools.drop_view_if_exists(cr, '%s'%(self._name.replace('.', '_')))
        cr.execute("""
                      CREATE OR REPLACE VIEW %s AS ( %s) 
        """%(self._name.replace('.', '_'), query) ) 
