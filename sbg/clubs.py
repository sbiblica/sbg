# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import datetime
import time
import sys
#sys.path.append("C:\\Archivos de programa\\OpenERP Web\\python25\\Lib\\site-packages\\pyodbc-2.1.7-py2.5-win32.egg")
#import pyodbc
import openerp.addons.decimal_precision as dp

class sbg_clubs(osv.osv):
    _name = 'sbg.clubs'
    _description = 'Clubs'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=31, required=True),
        'nombre': fields.char('Nombre del Club', size=60, required=True),
        'valor_cuota': fields.float('Valor de la cuota', digits_compute=dp.get_precision('Account'), required=True),
        'cantidad_donaciones_mes': fields.integer('Cantidad de donaciones al mes', required=True),
        'cantidad_pagos_anual': fields.integer('Cantidad de pagos anuales', required=True),
        'pagos_continuos': fields.integer('Cantidad de cuotas continuas para aplicar', required=True)
    }
    _defaults = {
        'valor_cuota': lambda *a: 30,
        'cantidad_donaciones_mes': lambda *a: 1,
        'cantidad_pagos_anual': lambda *a: 12,
        'pagos_continuos': lambda *a: 3
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_clubs()

class sbg_socios_clubs(osv.osv):
    _name = 'sbg.socios_clubs'
    _description = 'Clubs a los que perteneces el Socio'
    _rec_name = 'nombre_club'

    def onchange_club_id(self, cr, uid, ids, club_id):
        club = self.pool.get('sbg.clubs').browse(cr, uid, club_id)

        result = {'value': {
            'valor_cuota': club['valor_cuota'],
            'cantidad_donaciones_mes': club['cantidad_donaciones_mes'],
            'cantidad_pagos_anual': club['cantidad_pagos_anual'],
            'pagos_continuos': club['pagos_continuos']
            }
        }
        return result

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null', select=True, help="Keep empty for a private address, not related to partner."),
        'club_id': fields.many2one('sbg.clubs', 'Club al que pertenece', required=True),
        'nombre_club': fields.related('club_id', 'nombre', type='char', string='Club'),
        'valor_cuota': fields.float('Valor de la cuota', digits=(5,2), required=True),
        'cantidad_donaciones_mes': fields.integer('Cantidad de donaciones al mes', required=True),
        'cantidad_pagos_anual': fields.integer('Cantidad de pagos anuales', required=True),
        'pagos_continuos': fields.integer('Cantidad de cuotas continuas para aplicar', required=True),
        'fecha_inscripcion': fields.date('Fecha de Inscripcion al Club', required=True),
        'configuracion': fields.one2many('sbg.socios_clubs_configuracion', 'socio_clubs_id', 'Configuracion'),
    }
    _defaults = {
        'fecha_inscripcion': lambda *a: '1990-01-01',
    }

    _order = 'id desc'
sbg_socios_clubs()


class sbg_socios_clubs_configuracion(osv.osv):
    _name = 'sbg.socios_clubs_configuracion'
    _description = 'Configuracion de los Clubs a los que perteneces el Socio'
    _rec_name = 'cantidad_donaciones_mes'

    def onchange_fecha_configuracion(self, cr, uid, ids, partner_id, socio_clubs_id):

        result = {'value': {
            'partner_id': partner_id,
            'socio_clubs_id': socio_clubs_id
            }
        }
        return result

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='set null', select=True, help="Keep empty for a private address, not related to partner."),
        'socio_clubs_id': fields.many2one('sbg.socios_clubs', 'Clubs asignados al socio', required=True),
        'cantidad_donaciones_mes': fields.integer('Cantidad de donaciones al mes', required=True),
        'cantidad_pagos_anual': fields.selection([('12','12'),('6','6'),('4','4'),('2','2'),('1','1')], 'Cantidad de pagos anuales', required=True),
        'fecha_configuracion': fields.date('Fecha de configuracion', required=True),
    }
    _defaults = {
        'cantidad_donaciones_mes': lambda *a: 1,
        'cantidad_pagos_anual': lambda *a: '12',
    }
    _order = 'fecha_configuracion desc'
sbg_socios_clubs_configuracion()
