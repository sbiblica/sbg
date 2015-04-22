# -*- encoding: utf-8 -*-

import time
import datetime
from openerp.report import report_sxw

class compras_reporte(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(compras_reporte, self).__init__(cr, uid, name, context=context)
        self.totales = {}
        self.folioActual = -1
        self.localcontext.update( {
            'time': time,
            'datetime': datetime,
            'lineas': self.lineas,
            'totales': self.totales,
            'folio': self.folio,
        })
        self.context = context
        self.cr = cr

    def folio(self, datos):

        if self.folioActual < 0:
            if datos[0].folio_inicial <= 0:
                self.folioActual = 1
            else:
                self.folioActual = datos[0].folio_inicial 
        else:
            self.folioActual += 1

        return self.folioActual

    def lineas(self, datos):
        self.totales['compra'] = {'neto':0,'iva':0,'total':0}
        self.totales['servicio'] = {'neto':0,'iva':0,'total':0}
        self.totales['importacion'] = {'neto':0,'iva':0,'total':0}
        self.totales['combustible'] = {'neto':0,'iva':0,'total':0}
        self.totales['pequenio_contribuyente'] = {'neto':0,'iva':0,'total':0}

        #having sum(case when line.tax_code_id = %s then line.debit else 0 end) - sum(case when line.tax_code_id = %s then line.credit else 0 end) <> 0 \
        self.cr.execute("select \
                invoice.date_invoice, \
                invoice.journal_id, \
                invoice.tipo_gasto, \
                invoice.reference, \
                invoice.type, \
                invoice.pequenio_contribuyente, \
                partner.name, \
                partner.vat, \
                invoice.amount_total, \
                sum(case when line.tax_code_id = %s then line.debit else 0 end) - sum(case when line.tax_code_id = %s then line.credit else 0 end) as total_impuesto, \
                sum(case when line.tax_code_id = %s then line.debit else 0 end) - sum(case when line.tax_code_id = %s then line.credit else 0 end) as total_base \
            from account_move_line line join account_invoice invoice on(line.move_id = invoice.move_id) \
                join res_partner partner on(invoice.partner_id = partner.id) \
            where invoice.state in ('open','paid') and \
                invoice.journal_id in ("+','.join([str(d.id) for d in datos.diarios_id])+") and \
                line.period_id in ("+','.join([str(p.id) for p in datos.periodos_id])+") \
            group by invoice.date_invoice, invoice.journal_id, invoice.tipo_gasto, invoice.reference, invoice.type, invoice.pequenio_contribuyente, partner.name, partner.vat, invoice.amount_total \
            order by invoice.type, date_invoice",
            (datos.impuesto_id.id, datos.impuesto_id.id, datos.base_id.id, datos.base_id.id))

        lineas = self.cr.dictfetchall()

        for l in lineas:

            if l['pequenio_contribuyente'] == True:
                l['total_base'] = l['amount_total']
                self.totales['pequenio_contribuyente']['neto'] += l['total_base']
                self.totales['pequenio_contribuyente']['iva'] += l['total_impuesto']
                self.totales['pequenio_contribuyente']['total'] += l['total_base']+l['total_impuesto']

            self.totales[l['tipo_gasto']]['neto'] += l['total_base']
            self.totales[l['tipo_gasto']]['iva'] += l['total_impuesto']
            self.totales[l['tipo_gasto']]['total'] += l['total_base']+l['total_impuesto']

        return lineas

report_sxw.report_sxw('report.compras_reporte', 'l10n_gt_extra.asistente_compras_reporte', 'addons/l10n_gt_extra/report/compras_reporte.rml', parser=compras_reporte, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
