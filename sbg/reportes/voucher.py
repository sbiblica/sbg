 #-*- coding: utf-8 -*-
import time
from openerp.report import report_sxw
from .. import util
import locale

class voucher(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(voucher, self).__init__(cr, uid, name, context=context)
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        self.localcontext.update({
            'time': time,
            'factura': self.factura,
            'util': util,
            'locale': locale,
        })
        self.context = context
        self.uid = uid
        self.cr = cr
        letras = ''

    def factura(self, diario, linea):
        result = ""

        if linea.reconcile_id:

            for l in linea.reconcile_id.line_id:
                if l.journal_id.id != diario.id:
                    result += l.ref+" "

            for l in linea.reconcile_id.line_partial_ids:
                if l.journal_id.id != diario.id:
                    result += l.ref

        return result

report_sxw.report_sxw('report.sbg.voucher', 'account.voucher', 'addons/sbg/reportes/voucher.rml', parser=voucher)
