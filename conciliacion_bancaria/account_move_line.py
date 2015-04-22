# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class account_move_line(osv.osv):
    _inherit = 'account.move.line'

    _columns = {
        'conciliado_banco': fields.one2many('conciliacion.linea', 'move_id', 'Conciliado con banco'),
        'periodo_conciliado_banco': fields.related('conciliado_banco', 'period_id', type="many2one", relation="account.period", string='Periodo conciliado', help="El período en el que se concilió"),
    }
account_move_line()
