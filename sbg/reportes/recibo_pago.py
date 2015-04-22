# -*- encoding: utf-8 -*-

import time
import datetime
from openerp.report import report_sxw

from openerp.osv import osv
from openerp.osv import fields

def fecha(valor):
    return datetime.datetime.strptime(valor, '%Y-%m-%d')


class Debugear():
    _name = 'debugear'
    _columns = {
        'fecha': fields.char('Fecha', size=60),
    }

    def init(self, o):
        return ''

Debugear()


class payment_order_report_len1(report_sxw.rml_parse):
    def hola(self, cr, uid, name, context):

        debugear = Debugear()
        
        super(payment_order_report_len1, self).__init__(cr, uid, name, context)
        self.localcontext.update( {
            'time': time,
            'debugear': debugear,
        })


    def __init__(self, cr, uid, name, context):

        debugear = Debugear()

        super(payment_order_report_len1, self).__init__(cr, uid, name, context)
        self.totales = {'devengado':0, 'descuentos':0}
        self.localcontext.update({
                'convert': self.convert,
                'get_month': self.get_month,
                'get_earnings': self.get_earnings,
                'get_deductions':self.get_deductions,
                'get_leave':self.get_leave,
                'get_others':self.get_others,
                'debugear': debugear,
		'totales': self.totales,
                })

    def convert(self, amount, cur):
        amt_en = amount_to_text_en.amount_to_text(amount, 'en', cur)
        return amt_en

    def get_others(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].category_id.type in ('advance', 'loan', 'otherpay', 'otherdeduct', 'installment'):
                ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res

    def get_leave(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
        for id in range(len(obj)):
            if obj[id].type == 'leaves':
                ids.append(obj[id].id)
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res

    def get_earnings(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
	self.totales['devengado'] = 0
        for id in range(len(obj)):
            if obj[id].code == 'SQ' or (obj[id].category_id.type == 'allowance' and obj[id].type != 'leaves'):
                ids.append(obj[id].id)
		self.totales['devengado'] += obj[id].total
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)

        return res

    def get_deductions(self, obj):
        payslip_line = self.pool.get('hr.payslip.line')
        res = []
        ids = []
	self.totales['descuentos'] = 0
        for id in range(len(obj)):
            if obj[id].category_id.type == 'deduction' and obj[id].type != 'leaves':
		if obj[id].code != 'SQ':
                    ids.append(obj[id].id)
		    self.totales['descuentos'] += obj[id].total
        if ids:
            res = payslip_line.browse(self.cr, self.uid, ids)
        return res
   

    def get_month(self, obj):
        res = {
                'mname':''
        }
        date = datetime.strptime(obj.date, '%Y-%m-%d')
        res['mname']= date.strftime('%B')+"-"+date.strftime('%Y')
        return res['mname']

report_sxw.report_sxw('report.recibo.pago', 'hr.payslip', 'mis_modulos/sbg/reportes/recibo_pago.rml', parser=payment_order_report_len1, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
