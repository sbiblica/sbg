# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import datetime

class sbg_como_nos_conocio(osv.osv):
    _name = 'sbg.como_nos_conocio'
    _description = 'Como nos conocio'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Como nos conocio', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_como_nos_conocio()


class sbg_profesion(osv.osv):
    _name = 'sbg.profesion'
    _description = 'Profesion de los socios'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Profesion', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_profesion()


class sbg_religion(osv.osv):
    _name = 'sbg.religion'
    _description = 'Religion'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Religion', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_religion()


class sbg_puesto_desempena(osv.osv):
    _name = 'sbg.puesto_desempena'
    _description = 'Puesto que desempena'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Puesto', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_puesto_desempena()


class sbg_estado_civil(osv.osv):
    _name = 'sbg.estado_civil'
    _description = 'Estado Civil'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Estado Civil', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_estado_civil()


class sbg_denominacion_iglesia(osv.osv):
    _name = 'sbg.denominacion_iglesia'
    _description = 'Denominacion de la Iglesia'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Denominacion de la Iglesia', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_denominacion_iglesia()


class sbg_codigo_metodo_envio(osv.osv):
    _name = 'sbg.codigo_metodo_envio'
    _description = 'Codigo de metodo de envio'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Codigo de metodo de envio', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_codigo_metodo_envio()


class sbg_transporte(osv.osv):
    _name = 'sbg.transporte'
    _description = 'Transporte'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Nombre', size=100, required=True),
        'direccion': fields.char('Direccion', size=1000, required=True),
        'telefono': fields.char('Telefono', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_transporte()


class sbg_diosesis(osv.osv):
    _name = 'sbg.diosesis'
    _description = 'Jerarquias Eclesiasticas'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Jerarquias Eclesiasticas', size=40, required=True),
    }
    _order = 'nombre'
    _sql_constraints = [
        ('code_uniq', 'unique (codigo)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_diosesis()


class sbg_dias_semana(osv.osv):
    _name = 'sbg.dias_semana'
    _description = 'Dias de la semana'
    _rec_name = 'nombre'
    _columns = {
        'dias_semana_id': fields.char('Codigo', size=10, required=True),
        'nombre': fields.char('Dia', size=40, required=True),
    }
    _order = 'dias_semana_id'
    _sql_constraints = [
        ('code_uniq', 'unique (dias_semana_id)', 'El codigo que ingreso ya existe. Intente de nuevo')
    ]
sbg_dias_semana()

class sbg_regiones(osv.osv):
    _name = 'sbg.regiones'
    _description = 'Regiones'
    _rec_name = 'nombre'
    _columns = {
        'codigo': fields.char('Codigo', size=5, required=True),
        'nombre': fields.char('Region', size=40, required=True),
    }
    _order = 'codigo'
sbg_regiones()

class sbg_departamentos(osv.osv):
    _name = 'sbg.departamentos'
    _description = 'Departamentos'
    _rec_name = 'nombre'
    _columns = {
        'region_id': fields.many2one('sbg.regiones', 'Region', required=True),
        'codigo': fields.char('Codigo', size=5, required=True),
        'nombre': fields.char('Departamento', size=40, required=True),
    }
    _order = 'codigo'
sbg_departamentos()

class sbg_municipios(osv.osv):
    _name = 'sbg.municipios'
    _description = 'Municipios'
    _rec_name = 'nombre'
    _columns = {
        'region_id': fields.many2one('sbg.regiones', 'Region', required=True),
        'departamento_id': fields.many2one('sbg.departamentos', 'Departamento', required=True),
        'codigo': fields.char('Codigo', size=5, required=True),
        'nombre': fields.char('Municipio', size=40, required=True),
    }
    _order = 'codigo'
sbg_municipios()
