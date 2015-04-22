# -*- coding: utf-8 -*-

from openerp.osv import osv
from openerp.tools.translate import _

class account_move_line_conciliar(osv.osv_memory):

    _name = "account.move.line.conciliar"
    _description = "Banco: conciliar apuntes"

    def conciliar(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        self.pool.get('account.move.line').write(cr, uid, context['active_ids'], {'conciliado':True})

        return {'type': 'ir.actions.act_window_close'}

account_move_line_conciliar()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
