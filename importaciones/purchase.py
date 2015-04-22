# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class purchase(osv.osv):
    _inherit = 'purchase.order'

    _columns = {
        'poliza_id': fields.many2one('importaciones.poliza', 'Poliza', ondelete='set null'),
    }
purchase()
