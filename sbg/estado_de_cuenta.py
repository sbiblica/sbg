from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class sbg_socios_estado_de_cuenta(osv.osv):
    _name = 'sbg.socios_estado_de_cuenta'
    _description = 'Estado de cuenta'
    _rec_name = 'partner_id'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null', select=True, help="Keep empty for a private address, not related to partner."),
        'mensualidad': fields.integer('Mensualidad pagada'),
        'sopnumbe': fields.char('Numero de recibo', size=10),
        'docdate': fields.date('Fecha', size=10, required=True),
        'docid': fields.char('Codigo del recibo', size=60),
        'club_id': fields.many2one('sbg.clubs', 'Club al que pertenece', required=True),
        'valor_cuota': fields.float('Valor de la cuota', digits_compute=dp.get_precision('Account')),
        'subtotal': fields.float('Subtotal', digits_compute=dp.get_precision('Account')),
        'cantidad_donaciones': fields.integer('Cantidad de donaciones'),
        'estado': fields.selection([('Pagada','Pagada'),('Perdonada','Perdonada'),('Pendiente','Pendiente')], 'Estado'),
#        'borrar': fields.boolean('borrar'),
    }
    _order = 'mensualidad desc, club_id asc, sopnumbe desc'
sbg_socios_estado_de_cuenta()


class sbg_socios_cuotas_perdonadas(osv.osv):
    _name = 'sbg.socios_cuotas_perdonadas'
    _description = 'Perdonar Cuotas'
    _rec_name = 'partner_id'
    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null', select=True, help="Keep empty for a private address, not related to partner."),
        'mensualidad': fields.integer('Mensualidad'),
        'docdate': fields.date('Fecha', size=10, required=True),
        'club_id': fields.many2one('sbg.clubs', 'Club al que pertenece', required=True),
        'cantidad_donaciones': fields.integer('Cantidad de donaciones'),
        'estado': fields.selection([('Perdonada','Perdonada'),('Pendiente','Pendiente')], 'Estado'),
        'borrar': fields.boolean('borrar'),
    }
    _defaults = {
        'borrar': lambda *a: False,
    }
    _order = 'mensualidad desc, club_id asc'
sbg_socios_cuotas_perdonadas()

