# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class account_bank_statement(osv.osv):
    _inherit = 'account.bank.statement'

    _columns = {
        'bolson_id': fields.many2one('sbg.bolson', 'Liquidacion'),
    }
account_bank_statement()
