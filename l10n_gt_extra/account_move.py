# -*  encoding: utf-8 -*-

from openerp.osv import osv
from openerp.osv import fields

class account_move(osv.osv):
    _inherit = "account.move"
    
    _columns = {
        'tipo': fields.selection((('nota_credito', 'Nota de crédito'), ('nota_debito', 'Nota de débito'), ('nota_credito', 'Nota de crédito'), ('exencion', 'Constancia de exención'), ('retencion', 'Constancia de retención de IVA')), 'Tipo'),
    }
account_move()
