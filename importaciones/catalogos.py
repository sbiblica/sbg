# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class tipo_gasto(osv.osv):
    _name = 'importaciones.tipo_gasto'
    _description = 'Tipos de gastos'
    _columns = {
        'name': fields.char('Nombre', size=60, required=True),
    }
tipo_gasto()
