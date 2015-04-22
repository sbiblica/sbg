# -*- encoding: utf-8 -*-

import time
import datetime
from openerp.report import report_sxw
from datetime import datetime

class libro_salarios_reporte(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(libro_salarios_reporte, self).__init__(cr, uid, name, context)
        
        self.localcontext.update({
            'time': time,
            'periodos':self.periodos,
            'get_no': self.get_no,
            'encabezado': self.encabezado,
        })
        self.no = 0

    def get_no(self):
        self.no += 1
        return self.no

    def encabezado(self, obj):

        nacimiento = datetime.strptime(obj.employee_id.birthday, '%Y-%m-%d')
        hoy = datetime.today()

        anios = hoy.year - nacimiento.year
        if hoy.month < nacimiento.month:
            anios -= 1
        elif hoy.month == nacimiento.month and hoy.day < nacimiento.day:
            anios -= 1

        if obj.employee_id.gender == 'male':
            genero = 'Masculino'
        else:
            genero = 'Femenino'

        contrato_ids = self.pool.get('hr.contract').search(self.cr, self.uid, [('employee_id', '=', obj.employee_id.id)])
        for contrato_id in contrato_ids:
            contrato = self.pool.get('hr.contract').browse(self.cr, self.uid, contrato_id)
            fecha_inicio = contrato.date_start
            fecha_fin = contrato.date_end


        if obj.numero_fila == 1:
            return {'nombre':obj.employee_id.name, 'anios': anios, 'genero': genero, 'nacionalidad': obj.employee_id.country_id.name, 'ocupacion': obj.employee_id.job_id.name, 'afiliacion_igss': obj.employee_id.ssnid, 'documento_identificacion': obj.employee_id.identification_id, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin}
        return {}


    def periodos(self, obj):
        per = []

        self.cr.execute("select to_char(p.date, 'YYYY-MM') from hr_employee e, hr_payslip p where e.id = p.employee_id and e.id = " + str(obj.employee_id.id) + " and p.register_id = " + str(obj.register_id.id) + " group by to_char(p.date, 'YYYY-MM') order by to_char(p.date, 'YYYY-MM')")

        for i in range(obj.numero_fila):
            per.append({'numero_orden': ' '})
        

        for row in self.cr.fetchall():
        
            periodo = row[0]

            self.cr.execute("select e.id, rr.name, '" + str(periodo) + "' as periodo, sum(p.basic)/2 as salario, sum(p.working_days)/2 as dias_trabajados, sum(p.basic)/2 as salario_ordinario, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p1, hr_payslip_line pl where pl.slip_id = p1.id and p1.employee_id = e.id and to_char(p1.date, 'YYYY-MM') = '" + str(periodo) + "' and pl.code = 'HE' ) as salario_extra_ordinario, sum(p.basic)/2 + sum(p.allounce) as salario_total, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p2, hr_payslip_line pl where pl.slip_id = p2.id and p2.employee_id = e.id and to_char(p2.date, 'YYYY-MM') = '" + str(periodo) + "' and pl.code = 'IGSS') as igss, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p3, hr_payslip_line pl where pl.slip_id = p3.id and p3.employee_id = e.id and to_char(p3.date, 'YYYY-MM') = '" + str(periodo) + "' and ( pl.code = 'SV' or pl.code = 'BT' or pl.code = 'LP' or pl.code = 'SC' or pl.code = 'CEL' or pl.code = 'SF' or pl.code = 'AT' or pl.code = 'ISR' or pl.code = 'AT1' or pl.code = 'LP2' or pl.code = 'SF' or pl.code = 'AT2' or pl.code = 'OD' ) ) as otras_deducciones_legales, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p4, hr_payslip_line pl where pl.slip_id = p4.id and p4.employee_id = e.id and to_char(p4.date, 'YYYY-MM') = '" + str(periodo) + "' and ( pl.code = 'SV' or pl.code = 'BT' or pl.code = 'LP' or pl.code = 'SC' or pl.code = 'CEL' or pl.code = 'SF' or pl.code = 'AT' or pl.code = 'ISR' or pl.code = 'AT1' or pl.code = 'LP2' or pl.code = 'SF' or pl.code = 'AT2' or pl.code = 'OD' or pl.code = 'IGSS' ) ) as total_deducciones, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p5, hr_payslip_line pl where pl.slip_id = p5.id and p5.employee_id = e.id and to_char(p5.date, 'YYYY-MM') = '" + str(periodo) + "' and (pl.code = 'BTR' or pl.code = 'B14' or pl.code = 'AG' ) ) as decreto_42_92, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p6, hr_payslip_line pl where pl.slip_id = p6.id and p6.employee_id = e.id and to_char(p6.date, 'YYYY-MM') = '" + str(periodo) + "' and pl.code = 'BI' ) as bonificacion_incentivo, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p7, hr_payslip_line pl where pl.slip_id = p7.id and p7.employee_id = e.id and to_char(p7.date, 'YYYY-MM') = '" + str(periodo) + "' and pl.code = 'CO' ) as comisiones, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p9, hr_payslip_line pl where pl.slip_id = p9.id and p9.employee_id = e.id and to_char(p9.date, 'YYYY-MM') = '" + str(periodo) + "' and pl.code = 'SA' ) as septimos_asuetos, (select CASE WHEN sum(pl.total) is null THEN 0 ELSE sum(pl.total) END from hr_payslip p9, hr_payslip_line pl where pl.slip_id = p9.id and p9.employee_id = e.id and to_char(p9.date, 'YYYY-MM') = '" + str(periodo) + "' and pl.code = 'VAC' ) vacaciones, sum(p.net) as liquido_recibir from hr_employee e, hr_payslip p, resource_resource rr where e.id = p.employee_id and rr.id = e.resource_id and e.id = " + str(obj.employee_id.id) + " and to_char(p.date, 'YYYY-MM') = '" + str(periodo) + "' and p.register_id = " + str(obj.register_id.id) + " group by e.id, rr.name, periodo, p.working_days order by periodo, rr.name")

            for row2 in self.cr.fetchall():

                res = {
                    'numero_orden': obj.numero_orden, 
                    'periodo': row[0], 
                    'salario': row2[3], 
                    'dias_trabajados': row2[4], 
                    'horas_ordinarias': '0.00', 
                    'horas_extra_ordinarias': '0.00', 
                    'salario_ordinario':row2[5], 
                    'salario_extra_ordinario':row2[6], 
                    'salario_total':row2[7], 
                    'igss':row2[8], 
                    'otras_deducciones_legales':row2[9], 
                    'total_deducciones':row2[10], 
                    'decreto_42_92':row2[11], 
                    'bonificacion_incentivo':row2[12], 
                    'comisiones': row2[13],
                    'septimos_asuetos': row2[14],
                    'vacaciones': row2[15],
                    'liquido_recibir':row2[16],
                }

                per.append(res)

        return per

report_sxw.report_sxw('report.libro.salarios.reporte', 'sbg.asistente_libro_salarios', 'mis_modulos/sbg/reportes/libro_salarios_reporte.rml', parser=libro_salarios_reporte, header=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
