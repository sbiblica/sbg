# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from datetime import datetime
import util

class account_journal(osv.osv):
    _inherit = 'account.journal'

    _columns = {
        'punto_de_venta': fields.boolean('Punto de venta'),
    }
account_journal()

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    def _dia(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for move_line in self.browse(cr, uid, ids):
            result[move_line.id] = util.a_fecha(move_line.date).day
        return result

    def _dia_vencidos(self, cr, uid, ids, field_name, arg, context):
        result = {}
        for move_line in self.browse(cr, uid, ids):
            if move_line.date:
                result[move_line.id] = (datetime.today() - util.a_fecha(move_line.date)).days
            else:
                result[move_line.id] = 0
        return result

    _columns = {
        'comercial': fields.related('partner_id', 'user_id', type='many2one', relation='res.users', string='Comercial', store=False),
        'dia': fields.function(_dia, type='integer', method=True, string='Dia', store=True),
        'conciliado': fields.boolean(string='Conciliado'),
        'dias_vencidos': fields.function(_dia_vencidos, type='integer', method=True, string='Dias vencidos'),
    }
account_move_line()

