# -*- coding: utf-8 -*-

######################################################################
#
#  Note: Program metadata is available in /__init__.py
#
######################################################################

from openerp.osv import fields, osv
from openerp import tools

class account_aging_customer(osv.osv):
    _name = 'partner.aging.customer'
    _auto = False

    def read_group(self, cr, uid, domain, fields, groupby, offset=0, limit=None, context=None, orderby=False):
        if 'max_days_overdue' in fields:
            fields.remove('max_days_overdue')
        return super(account_aging_customer, self).read_group(cr, uid, domain, fields, groupby, offset, limit=limit, context=context, orderby=orderby)

    def docopen(self, cr, uid, ids, context=None):
        """
        @description  Open document (invoice or payment) related to the
                      unapplied payment or outstanding balance on this line
        """

        if not context:
            context = {}
        active_id = context.get('active_id')
        models = self.pool.get('ir.model.data')
        #Get this line's invoice id
        inv_id = self.browse(cr, uid, ids[0]).invoice_id.id
        
        #if this is an unapplied payment(all unapplied payments hard-coded to -999), 
        #get the referenced voucher
        if inv_id == -999:
            ref = self.browse(cr, uid, ids[0]).invoice_ref
            payment_pool = self.pool.get('account.voucher')
            #Get referenced customer payment (invoice_ref field is actually a payment for these)
            voucher_id = payment_pool.search(cr, uid, [('number','=',ref)])[0]
            view = models.get_object_reference(cr, uid, 'account_voucher', 'view_voucher_form')
            #Set values for form
            view_id = view and view[1] or False
            name = 'Customer Payments'
            res_model = 'account.voucher'
            ctx = "{}"
            doc_id = voucher_id
            
        #otherwise get the invoice
        else:
            view = models.get_object_reference(cr, uid, 'account', 'invoice_form')
            view_id = view and view[1] or False
            name = 'Customer Invoices'
            res_model = 'account.invoice'
            ctx = "{'type':'out_invoice'}"
            doc_id = inv_id
    
        if not doc_id:
            return {}
        
        #Open up the document's form
        return {
            'name': (name),
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': [view_id],
            'res_model': res_model,
            'context': ctx,
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': doc_id,
        }

    _columns = {
        'partner_id': fields.many2one('res.partner', u'Partner', readonly=True),
        'partner_name': fields.text('Name', readonly=True),
        'comercial_id': fields.many2one('res.partner', 'Comercial', readonly=True),
        'comercial_name': fields.text('Comercial Name', readonly=True),
        'avg_days_overdue': fields.integer(u'Avg Days Overdue', readonly=True),
        'date': fields.date(u'Date', readonly=True),
        'date_due': fields.date(u'Due Date', readonly=True),
        'total': fields.float(u'Total', readonly=True),
        'not_due': fields.float(u'Not Due Yet', readonly=True),
        'current': fields.float(u'Current', readonly=True),
        'days_due_01to30': fields.float(u'1/30', readonly=True),
        'days_due_31to60': fields.float(u'31/60', readonly=True),
        'days_due_61to90': fields.float(u'61/90', readonly=True),
        'days_due_91to120': fields.float(u'91/120', readonly=True),
        'days_due_121togr': fields.float(u'+121', readonly=True),
        'max_days_overdue': fields.integer(u'Days Outstanding',readonly=True),
        'invoice_ref': fields.char('Our Invoice', size=25, readonly=True),
        'invoice_id': fields.many2one('account.invoice', 'Invoice', readonly=True),
        'comment': fields.text('Notes', readonly=True),
        'salesman': fields.many2one('res.users', u'Sales Rep', readonly=True),
        'unapp_credits': fields.float(u'Unapplied Credits', readonly=True),
        'unapp_cash': fields.float(u'Unapplied Cash', readonly=True),
     }

    _order = 'partner_name'

    def init(self, cr):
        """
        @author       Ursa Information Systems
        @description  Update table on load with latest aging information
        @modified      2015-03-11
        """

        query = """ 
                Select sq2.id,sq2.partner_id,sq2.partner_name,
        ruc.id AS comercial_id ,ruc.name AS comercial_name,
        sq2.salesman,sq2.avg_days_overdue,sq2.date,sq2.date_due,sq2.total,sq2.unapp_cash,
	sq2.days_due_01to30,
	sq2.days_due_31to60,
	sq2.days_due_61to90,
	sq2.days_due_91to120,
	sq2.days_due_121togr,
	sq2.max_days_overdue,
	sq2.not_due,
	sq2.current,
	sq2.invoice_ref,
	sq2.invoice_id,
	sq2.comment,
	sq2.unapp_credits

	from (
select aml.id, 
partner_id, 
NULL AS partner_name,
0 AS salesman, 
days_due AS avg_days_overdue, NULL as date, date as date_due,                
                
                CASE WHEN reconcile_partial_id is not NULL THEN debit-
                    (select sum(l.credit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (debit-credit) END AS TOTAL, 
                    
                    0 AS unapp_cash,
                    0 AS "days_due_01to30",
                    
                CASE WHEN (days_due BETWEEN 31 and 60) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN debit-
                        (select sum(l.credit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (debit-credit) END
                ELSE 0 END AS days_due_31to60, 
                
                CASE WHEN (days_due BETWEEN 61 and 90) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN debit-
                        (select sum(l.credit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (debit-credit) END
                ELSE 0 END AS days_due_61to90,
                
                CASE WHEN (days_due BETWEEN 91 and 120) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN debit-
                        (select sum(l.credit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (debit-credit) END
                ELSE 0 END AS days_due_91to120,
                
                CASE WHEN (days_due >= 121) THEN                     
                    CASE WHEN reconcile_partial_id is not NULL THEN debit-
                        (select sum(l.credit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (debit-credit) END
                ELSE 0 END AS days_due_121togr,
                
                CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                
                CASE WHEN (days_due < 31) THEN 
                    CASE WHEN reconcile_partial_id is not NULL THEN debit-
                        (select sum(l.credit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (debit-credit) END
                ELSE 0 END AS not_due,  
                0 AS current,                
                     
                name AS invoice_ref, -14156 as invoice_id, NULL AS comment, 
                
                CASE WHEN reconcile_partial_id is not NULL THEN debit-
                        (select sum(l.credit) from account_move_line l where l.reconcile_partial_id = aml.reconcile_partial_id) ELSE (debit-credit)
                END AS unapp_credits

                   from account_move_line aml 
                   
                INNER JOIN
                  ( SELECT aml2.id, (current_date - aml2.date) AS days_due  FROM account_move_line aml2 ) DaysDue
                ON DaysDue.id = aml.id
                where
                    open_ar = 't'                
                    AND reconcile_id is NULL 
                    AND account_id in (select id from account_account where type = 'receivable')


                UNION       
                select id, partner_id, partner_name ,salesman, avg_days_overdue, oldest_invoice_date as date, date_due, total, unapp_cash, days_due_01to30, days_due_31to60, days_due_61to90, days_due_91to120, days_due_121togr, max_days_overdue, not_due, current, invoice_ref, invoice_id, comment, unapp_credits from account_voucher_customer_unapplied 


                UNION 

            
                SELECT id, partner_id, partner_name,salesman, avg_days_overdue, date, date_due, total, unapp_cash,
                       days_due_01to30, days_due_31to60, days_due_61to90, days_due_91to120, days_due_121togr, max_days_overdue, not_due, current, invoice_ref, invoice_id, comment, unapp_credits 
                       from (

                --------++--------
                SELECT l.id as id, 
                l.partner_id as partner_id, 
                res_partner.name as "partner_name",
                --ru.id AS comercial_id,
                --ru.name comercial_name,
                ai.user_id as salesman, 

                    days_due as "avg_days_overdue", l.date as "date",
                    CASE WHEN ai.id is not null THEN ai.date_due ElSE l.date END as "date_due",
                    CASE WHEN ai.type = 'out_refund' AND ai.id is not null THEN -1*ai.residual ELSE ai.residual
                         END as "total",
                    0 AS "unapp_cash",
                    0 AS "days_due_01to30",
                    CASE WHEN (days_due BETWEEN 31 AND  60) and ai.id is not null THEN
                             CASE WHEN ai.type = 'out_refund' THEN -1*ai.residual ELSE ai.residual END 
                         WHEN (days_due BETWEEN 31 and 60) and ai.id is null THEN l.debit - l.credit 
                         ELSE 0 END  AS "days_due_31to60",
                    CASE WHEN (days_due BETWEEN 61 AND  90) and ai.id is not null THEN 
                             CASE WHEN ai.type = 'out_refund' THEN -1*ai.residual ELSE ai.residual END 
                         WHEN (days_due BETWEEN 61 and 90) and ai.id is null THEN l.debit - l.credit 
                         ELSE 0 END  AS "days_due_61to90",
                    CASE WHEN (days_due BETWEEN 91 AND 120) and ai.id is not null THEN 
                             CASE WHEN ai.type = 'out_refund' THEN -1*ai.residual ELSE ai.residual END 
                         WHEN (days_due BETWEEN 91 and 120) and ai.id is null THEN l.debit - l.credit 
                         ELSE 0 END  AS "days_due_91to120",
                    CASE WHEN days_due >=121 and ai.id is not null THEN 
                             CASE WHEN ai.type = 'out_refund' THEN -1*ai.residual ELSE ai.residual END 
                         WHEN days_due >=121 and ai.id is null THEN l.debit-l.credit 
                         ELSE 0 END AS "days_due_121togr",
                    CASE when days_due < 0 THEN 0 ELSE days_due END as "max_days_overdue",
                    
                    CASE WHEN (days_due < 31) and ai.id is not null THEN 
                             CASE WHEN ai.type = 'out_refund' then -1*ai.residual ELSE ai.residual END 
                         WHEN (days_due < 1) and ai.id is null THEN l.debit - l.credit 
                         ELSE 0 END  AS "not_due",
                    0 AS current,                              
   
                    CASE WHEN ai.id is not null THEN ai.number ELSE l.ref END as "invoice_ref",
                    ai.id as "invoice_id", ai.comment,
                    CASE WHEN ai.type = 'out_refund' THEN -1*ai.residual END AS "unapp_credits"

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
                  AND (account_account.type IN ('receivable'))     
                  AND account_move.state = 'posted'
                  AND l.reconcile_id IS NULL
                  AND ai.state <> 'paid'
               --------++--------   
                ) sq ) sq2
	            LEFT JOIN res_partner rpc ON sq2.partner_id = rpc.id
	            LEFT JOIN (Select r.id AS user_id, p.id, p.name from res_users r JOIN res_partner p ON r.partner_id = p.id) ruc ON rpc.user_id = ruc.user_id
              """

        tools.drop_view_if_exists(cr, '%s' % (self._name.replace('.', '_')))
        cr.execute("""
                      CREATE OR REPLACE VIEW %s AS ( %s)
        """ % (self._name.replace('.', '_'), query))
