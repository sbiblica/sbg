# -*- encoding: utf-8 -*-

import time
import datetime
from openerp.report import report_sxw
import logging

class banco_reporte(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(banco_reporte, self).__init__(cr, uid, name, context)
        self.totales = {'debito':0, 'credito':0}
        self.totales_circulacion = {'debito':0, 'credito':0}
        self.localcontext.update( {
            'time': time,
            'datetime': datetime,
            'lineas': self.lineas,
            'lineas_circulacion': self.lineas_circulacion,
            'balance_final': self.balance_final,
            'totales': self.totales,
            'totales_circulacion': self.totales_circulacion,
        })
        self.lineas_result = None
        self.lineas_circulacion_result = None
        self.context = context
        self.cr = cr

    def lineas(self, datos):

        #
        # Solo ejecutar una vez este metodo
        #
        if self.lineas_result:
            return self.lineas_result

        fecha_desde = datos.periodo_desde.date_start
        fecha_hasta = datos.periodo_hasta.date_stop

        self.cr.execute('''select l.id
            from account_move_line l left join conciliacion_linea c on (l.id = c.move_id)
                left join account_period p on (c.period_id = p.id)
            where l.account_id = %s and
                p.date_start between %s and %s''', (datos.cuenta_bancaria_id.id, fecha_desde, fecha_hasta))
        lineas_id = [x[0] for x in self.cr.fetchall()]

        lineas = []

        for linea_id in lineas_id:

            linea = self.pool.get('account.move.line').browse(self.cr, self.uid, linea_id)

            detalle = {'fecha-iso':linea.date, 'fecha':datetime.datetime.strptime(linea.date, '%Y-%m-%d').strftime('%d%m%y'), 'documento':  linea.move_id.name if linea.move_id else '', 'nombre':linea.partner_id.name or '', 'concepto':(linea.ref if linea.ref else '')+linea.name, 'debito':linea.debit, 'credito':linea.credit, 'tipo':''}

            lineas.append(detalle)

        lineas.sort(reverse=True, key=lambda x:x['fecha-iso']+x['documento'])

        #
        # El balance de cada linea, el total de cheque y agregarle partida, si
        # es necesaria.
        #
        balance = self.balance_final(datos)['balance']
        for i in range(len(lineas)):

            if i > 0:
                balance = lineas[i-1]['balance'] + (-lineas[i-1]['debito'] + lineas[i-1]['credito'])
            lineas[i]['balance'] = balance


        #
        # Calcular los totales solo una vez.
        #
        for linea in lineas:
            self.totales['debito'] += linea['debito']
            self.totales['credito'] += linea['credito']

        lineas.sort(key=lambda x:x['fecha-iso']+x['documento'])
        self.lineas_result = lineas

        return self.lineas_result

    def lineas_circulacion(self, datos):

        #
        # Solo ejecutar una vez este metodo
        #
        if self.lineas_circulacion_result:
            return self.lineas_circulacion_result

        fecha_desde = datos.periodo_desde.fiscalyear_id.date_start
        fecha_hasta = datos.periodo_desde.date_stop

        self.cr.execute('''select l.id
            from account_move_line l left join conciliacion_linea c on (l.id = c.move_id)
                left join account_period p on (c.period_id = p.id)
            where l.account_id = %s and
                l.date between %s and %s and
                (p is null or p.date_start > %s)''', (datos.cuenta_bancaria_id.id, fecha_desde, fecha_hasta, fecha_hasta))
        lineas_id = [x[0] for x in self.cr.fetchall()]

        lineas = []

        for linea_id in lineas_id:

            linea = self.pool.get('account.move.line').browse(self.cr, self.uid, linea_id)

            detalle = {'fecha-iso':linea.date, 'fecha':datetime.datetime.strptime(linea.date, '%Y-%m-%d').strftime('%d%m%y'), 'documento':  linea.move_id.name if linea.move_id else '', 'nombre':linea.partner_id.name or '', 'concepto':(linea.ref if linea.ref else '')+linea.name, 'debito':linea.debit, 'credito':linea.credit, 'tipo':''}

            lineas.append(detalle)

        #
        # Calcular los totales solo una vez.
        #
        for linea in lineas:
            self.totales_circulacion['debito'] += linea['debito']
            self.totales_circulacion['credito'] += linea['credito']

        lineas.sort(key=lambda x:x['fecha-iso']+x['documento'])
        self.lineas_circulacion_result = lineas

        return self.lineas_circulacion_result

    def balance_final(self, datos):
        ctx = self.context.copy()

        fecha_desde = datos.periodo_desde.fiscalyear_id.date_start
        fecha_hasta = datos.periodo_desde.date_stop

        ctx['date_from'] = fecha_desde
        ctx['date_to'] = fecha_hasta

        cuenta = self.pool.get('account.account').read(self.cr, self.uid, datos.cuenta_bancaria_id.id, ['type','code','name','debit','credit','balance','parent_id'], ctx)

        self.cr.execute('''select sum(debit), sum(credit)
            from account_move_line l left join conciliacion_linea c on (l.id = c.move_id)
                left join account_period p on (c.period_id = p.id)
            where l.account_id = %s and
                l.date between %s and %s and
                (p is null or p.date_start > %s)''', (datos.cuenta_bancaria_id.id, fecha_desde, fecha_hasta, fecha_hasta))
        no_conciliado = 0

        logging.getLogger('banco').warn(cuenta['balance'])

        for linea in self.cr.fetchall():
            if linea[0] is not None and linea[1] is not None:
                no_conciliado = linea[0] - linea[1]
        cuenta['balance'] -= no_conciliado

        return cuenta

report_sxw.report_sxw('report.conciliacion_banco_reporte', 'conciliacion.banco_reporte_asistente', 'addons/conciliacion_bancaria/report/banco_reporte.rml', parser=banco_reporte, header=False)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
