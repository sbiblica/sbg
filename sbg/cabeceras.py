# -*- encoding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields

class cabeceras(osv.osv_memory):
    _name = 'sbg.cabeceras'

    def inicializar_cabeceras(self, cr, uid, ids, context=None):

        cr.execute("UPDATE hr_payslip_line SET amount=0 WHERE function_id is not null AND code in ('CEL','AT','BTR','HE','CO','OD')")

        return {
            'type': 'ir.actions.act_window_close',
        }

cabeceras()
