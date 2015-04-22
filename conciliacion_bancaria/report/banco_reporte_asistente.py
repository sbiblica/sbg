# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class banco_reporte_asistente(osv.osv_memory):
    _name = 'conciliacion.banco_reporte_asistente'
    _rec_name = 'cuenta_bancaria_id'
    _columns = {
        'cuenta_bancaria_id': fields.many2one('account.account', 'Cuenta', required=True),
        'ejercicios_fiscales': fields.many2many('account.fiscalyear', 'banco_anio_rel', 'banco_id', 'anio_id', 'Saldo incluyendo ejercicios fiscales'),
        'periodo_desde': fields.many2one('account.period', 'Período inicial', domain=[('state','<>','done')], required=True),
        'periodo_hasta': fields.many2one('account.period', 'Período final', domain=[('state','<>','done')], required=True),
        'circulacion': fields.boolean('En circulación'),
    }

    def _revisar_cuenta(self, cr, uid, context):
        if 'active_id' in context:
            return context['active_id']
        else:
            return None

    _defaults = {
        'cuenta_bancaria_id': _revisar_cuenta,
    }

    def reporte(self, cr, uid, ids, context=None):
        return {'type':'ir.actions.report.xml', 'report_name':'conciliacion_banco_reporte'}
banco_reporte_asistente()
