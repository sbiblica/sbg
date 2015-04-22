# -*- coding: utf-8 -*-

from openerp.osv import osv, fields

class res_company(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'poliza_secuencia_id': fields.many2one('ir.sequence', 'Secuencia poliza'),
    }
res_company()
