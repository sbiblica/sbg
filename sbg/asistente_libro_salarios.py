# -*- encoding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields
import time

class asistente_libro_salarios(osv.osv_memory):
    _name = 'sbg.asistente_libro_salarios'
    _rec_name = 'numero_fila'
    _columns = {
        'employee_id':fields.many2one('hr.employee', 'Empleado', required=True),
        'register_id': fields.many2one('hr.payroll.register', 'Registro de nomina', required=True),
        'numero_fila': fields.integer('Numero de fila', required=True),
        'numero_orden': fields.integer('Numero de orden', required=True),
    }

    def reporte(self, cr, uid, ids, context=None):
        return {'type':'ir.actions.report.xml', 'report_name':'libro_salarios_reporte'}

asistente_libro_salarios()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
