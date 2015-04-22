# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class hr_payroll_structure(osv.osv):
    _inherit = 'hr.payroll.structure'

    _columns = {
        'horas_ordinarias': fields.integer('Horas ordinarias'),
        'horas_extras': fields.integer('Horas extras'),
    }
hr_payroll_structure()

class hr_payslip(osv.osv):
    _inherit = 'hr.payslip'

    _columns = {
        'horas_ordinarias': fields.integer('Horas ordinarias'),
        'horas_extras': fields.integer('Horas extras'),
    }

    def compute_sheet(self, cr, uid, ids, context=None):
        result = super(hr_payslip, self).compute_sheet(cr, uid, ids, context) 
        for slip in self.browse(cr, uid, ids, context=context):
            self.pool.get('hr.payslip').write(cr, uid, [slip.id], {'horas_ordinarias':slip.deg_id.horas_ordinarias, 'horas_extras':slip.deg_id.horas_extras}, context=context)
        return result

hr_payslip()
