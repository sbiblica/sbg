# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv

class linea(osv.osv):
    _name = "conciliacion.linea"
    _description = "Relaciona un apunte contable con el periodo que fue conciliado"
    _columns = {
        'move_id': fields.many2one('account.move.line', 'Apunte', required=True, help="El apunte conciliado"),
        'period_id': fields.many2one('account.period', 'Periodo', required=True, help="El período en el que está conciliado"),
    }
    _sql_constraints = [
        ('move_uniq', 'unique (move_id)', 'Ese apunte ya fue conciliado.')
    ]
linea()

class conciliar(osv.osv):
    _name = "conciliacion.conciliar"
    _description = "Conciliar con banco"
    _columns = {
        'period_id': fields.many2one('account.period', 'Periodo', domain=[('state','<>','done')], help="El período en el que se hará conciliación"),
    }

    def conciliar(self, cr, uid, ids, context=None):
        for form in self.browse(cr, uid, ids, context=context):
            for line in self.pool.get('account.move.line').browse(cr, uid, context['active_ids'], context=context):
                if form.period_id:
                    self.pool.get('conciliacion.linea').create(cr, uid, {
                        'move_id': line.id,
                        'period_id': form.period_id.id
                    }, context=context)
        return {'type': 'ir.actions.act_window_close'}

    def desconciliar(self, cr, uid, ids, context=None):
        for form in self.browse(cr, uid, ids, context=context):
            for line in self.pool.get('account.move.line').browse(cr, uid, context['active_ids'], context=context):
                linea_ids = self.pool.get('conciliacion.linea').search(cr, uid, [('move_id','=',line.id)], context=context)
                self.pool.get('conciliacion.linea').unlink(cr, uid, linea_ids, context=context)
        return {'type': 'ir.actions.act_window_close'}

conciliar()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
