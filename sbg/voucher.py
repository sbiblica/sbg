# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class account_voucher(osv.osv):
    _inherit = 'account.voucher'

    def _conciliado(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for obj in self.browse(cr, uid, ids, context):
            result[obj.id] = True
            for l in obj.move_ids:
                if l.account_id.type == 'receivable' and not l.reconcile_id and not l.reconcile_partial_id:
                    result[obj.id] = False
                    break

        return result

    _columns = {
        'conciliado': fields.function(_conciliado, type='boolean', method=True, string='Conciliado'),
        #'bolson_id': fields.many2one('sbg.bolson', 'Liquidacion'),
        'fecha_recibo': fields.date('Fecha recibo'),
    }
account_voucher()
