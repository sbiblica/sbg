# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = 'account.invoice'

    _columns = {
        'bolson_id': fields.many2one('bolson.bolson', 'Liquidacion'),
    }
account_invoice()
