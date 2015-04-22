# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class documentos_asociados(osv.osv):
    _name = 'importaciones.documentos_asociados'
    _description = 'Documentos asociados'
    _rec_name = 'factura_id'

    _columns = {
        'poliza_id': fields.many2one('importaciones.poliza', 'Poliza'),
        'factura_id': fields.many2one('account.invoice', 'Documento', domain=[('type','=','in_invoice')]),
        'tipo_gasto_id': fields.many2one('importaciones.tipo_gasto', 'Tipo de gasto'),
    }
documentos_asociados()

class gastos_proyectados(osv.osv):
    _name = 'importaciones.gastos_proyectados'
    _description = 'Gastos proyectados de la importacion'
    _rec_name = 'valor'

    _columns = {
        'poliza_id': fields.many2one('importaciones.poliza', 'Poliza'),
        'valor': fields.float('Valor', digits_compute=dp.get_precision('Purchase Price')),
        'tipo_gasto_id': fields.many2one('importaciones.tipo_gasto', 'Tipo de gasto'),
    }
gastos_proyectados()
