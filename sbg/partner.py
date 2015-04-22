# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import datetime
import time

class res_partner(osv.osv):
    _inherit = 'res.partner'

    def calcular_estado_de_cuenta(self, cr, uid):
        result = {}

        cr.execute("select distinct(partner_id) from sbg_socios_clubs where partner_id is not null")

        x = 1
        for row in cr.fetchall():

            partner_id = row[0]

            x = x + 1

            cliente = self.pool.get('res.partner').browse(cr, uid, partner_id)
            cliente.socios_crear_estado_de_cuenta()

        return 1
    
    def socios_crear_estado_de_cuenta(self, cr, uid, ids, context):
        result = {}

        fecha_actual = datetime.date.today()
        dia_actual = fecha_actual.day
        mensualidad_actual = int(fecha_actual.strftime("%Y%m"))

        for cliente in self.pool.get('res.partner').browse(cr, uid, ids):

            cuotas_pendientes_ids = self.pool.get('sbg.socios_cuotas_perdonadas').search(cr, uid, [('partner_id', '=', cliente.id),('estado', '=', 'Pendiente')])
            self.pool.get('sbg.socios_cuotas_perdonadas').unlink(cr, uid, cuotas_pendientes_ids)

            socio_clubs_ids = self.pool.get('sbg.socios_clubs').search(cr, uid, [('partner_id', '=', cliente.id)])
            for socio_club_id in socio_clubs_ids:

                socio_club = self.pool.get('sbg.socios_clubs').browse(cr, uid, socio_club_id)
                club = socio_club.club_id

                socio_club_configuracion_ids = self.pool.get('sbg.socios_clubs_configuracion').search(cr, uid, [('partner_id', '=', cliente.id),('socio_clubs_id', '=', socio_club_id)],offset=0,limit=1,order='fecha_configuracion')

                if socio_club_configuracion_ids:

                    socio_club_configuracion = self.pool.get('sbg.socios_clubs_configuracion').browse(cr, uid, socio_club_configuracion_ids)[0]

                    vector_facturas = []

                    cuotas_ids = self.pool.get('sbg.socios_estado_de_cuenta').search(cr, uid, [('partner_id', '=', cliente.id), ('docdate', '<=', '2012-03-31'), ('estado', '=', 'Pagada'), ('club_id', '=', club.id), ('mensualidad','<','201204'), ('mensualidad','>','200501')], order='mensualidad asc')

                    for cuota_id in cuotas_ids:
                        cuota_obj = self.pool.get('sbg.socios_estado_de_cuenta').browse(cr, uid, cuota_id)
                        cuota = {
                            "sopnumbe": cuota_obj.sopnumbe,
                            "docdate": cuota_obj.docdate,
                            "docid": cuota_obj.docid,
                            "cantidad_donaciones": cuota_obj.cantidad_donaciones,
                            "valor_cuota": cuota_obj.valor_cuota
                        }
                        vector_facturas.append(cuota)

                    cuotas_ids = self.pool.get('sbg.socios_estado_de_cuenta').search(cr, uid, [('partner_id', '=', cliente.id), ('club_id', '=', club.id)])
                    self.pool.get('sbg.socios_estado_de_cuenta').unlink(cr, uid, cuotas_ids)

                    fecha_mensualidad_verificar = datetime.datetime.strptime(socio_club_configuracion.fecha_configuracion, '%Y-%m-%d')
                    mensualidad_verificar = int(fecha_mensualidad_verificar.strftime("%Y%m"))
                    mensualidad_revisar = mensualidad_verificar

                    dia_fecha_inscripcion = fecha_mensualidad_verificar.day

                    #Se accesa GP para obtener los pagos que ha realizado el socio para dicho club desde la fecha de inscripcion.
                    #cursor.execute("Select e.*,d.* From (Select soptype,sopnumbe,docdate,docid,custnmbr From Sop10100 Union Select soptype,sopnumbe,docdate,docid,custnmbr From SOP30200)E Join (Select sopnumbe,itemnmbr,unitprce, xtndprce,quantity  From SOP10200 Union Select sopnumbe,itemnmbr,unitprce, xtndprce,quantity   From SOP30300)D On e.sopnumbe = d.sopnumbe Where (E.docid='RECIBO DONGUATB' or E.docid='RECIBO DONGUATE' or E.docid='RECIBO DONXELA') and E.soptype = 3 And E.custnmbr=? AND D.itemnmbr=? AND convert(varchar(10),E.docdate,20) >= ? ORDER BY E.docdate asc, E.sopnumbe asc", str(cliente.ref), str(club.codigo), socio_club_configuracion.fecha_configuracion)
                    cr.execute("SELECT ai.number as sopnumbe, ai.date_invoice as docdate, '' as docid, ail.quantity as cantidad_donaciones, ail.price_unit as valor_cuota FROM account_invoice ai, account_invoice_line ail, product_product pp WHERE ai.id = ail.invoice_id AND ail.product_id = pp.id AND ai.partner_id = " + str(cliente.id) + " AND ai.date_invoice >= '" + str(socio_club_configuracion.fecha_configuracion) + "' AND pp.default_code = '" + club.codigo + "' AND (ai.state = 'open' OR ai.state = 'paid')")

                    for row in cr.fetchall():
                        cuota = {
                            "sopnumbe":row[0],
                            "docdate":row[1],
                            "docid":row[2],
                            "cantidad_donaciones":row[3],
                            "valor_cuota":row[4]
                        }
                        
                        vector_facturas.append(cuota)

                    for row in vector_facturas:

                        sopnumbe = row['sopnumbe']
                        docdate = str(row['docdate'])
                        docid = row['docid']
                        custnmbr = '1'
                        quantity = row['cantidad_donaciones']
                        unitprce = row['valor_cuota']

                        #Se revisa cual configuracion se utilizará para este pago en
                        #particular y se calculan los parametros necesarios.
                        no_registros_ingresar = 0
                        socio_club_configuracion_ids = self.pool.get('sbg.socios_clubs_configuracion').search(cr, uid, [('partner_id', '=', cliente.id),('socio_clubs_id', '=', socio_club_id)],order='fecha_configuracion desc')
                        for socio_club_configuracion_id in socio_club_configuracion_ids:
                            socio_club_configuracion = self.pool.get('sbg.socios_clubs_configuracion').browse(cr, uid, socio_club_configuracion_id)

                            if docdate >= str(socio_club_configuracion.fecha_configuracion):
                                frecuencia_pagos = 12 / int(socio_club_configuracion.cantidad_pagos_anual)

                                cantidad_donaciones_mes = socio_club_configuracion.cantidad_donaciones_mes

                                #El socio tiene definido cuantas cuotas hara al mes. Por lo tanto, para calcular la cantidad de
                                #registros que iran en el objeto estado de cuenta, se hace el siguiente calculo
                                no_registros_ingresar = int(quantity / socio_club_configuracion.cantidad_donaciones_mes)

                                #Se revisa si la cantidad de cuotas pagadas no corresponde a un multiplo de las cuotas que se
                                #hacen mensualmente. Si esto sucede, hay que agregar el registro al objeto estado de cuenta
                                #pero habra que agregar un registro adicional en la misma mensualidad y con estado pendiente
                                #con las cuotas que hacen falta.
                                cuotas_incompletas = 0
                                if (quantity % socio_club_configuracion.cantidad_donaciones_mes) != 0:
                                    if quantity > socio_club_configuracion.cantidad_donaciones_mes:
                                        cuotas_incompletas = quantity % socio_club_configuracion.cantidad_donaciones_mes
                                    else:
                                        cuotas_incompletas = socio_club_configuracion.cantidad_donaciones_mes - quantity

                                if cuotas_incompletas:
                                    no_registros_ingresar = no_registros_ingresar + 1

                        if no_registros_ingresar > 0:

                            #Empieza la busqueda de una mensualidad donde colocar la cuota pagada, empezando desde la 
                            #mensualidad mensualidad_revisar, la cual ha sido calculada con anticipacion. 
                            registros_ingresados = 0
                            buscar_posicion = True
                            while buscar_posicion:

                                cuota_perdonada_id = self.pool.get('sbg.socios_cuotas_perdonadas').search(cr, uid, [('partner_id', '=', cliente.id),('club_id', '=', club.id),('mensualidad', '=', mensualidad_revisar)])

                                #Si en esta mensualidad ya existe un registro en el objeto de cuotas perdonadas, hay que 
                                #revisar si es un registro con estado pendiente. Si es este el caso, entonces en esta 
                                #mensualidad si se puede agregar la cuota pagada en el objeto estado de cuenta. Si el estado
                                #es perdonado, en la siguiente repeticion del ciclo se revisara la siguiente mensualidad.
                                if cuota_perdonada_id:

                                    cuota_perdonada = self.pool.get('sbg.socios_cuotas_perdonadas').browse(cr, uid, cuota_perdonada_id)[0]
                                    if cuota_perdonada.estado == 'Pendiente':

                                        #Se crea el nuevo registro con la cuota pagada en el objeto estado de cuenta
                                        nuevo_registro_id = self.pool.get("sbg.socios_estado_de_cuenta").create(cr, uid, {'partner_id':cliente.id,'mensualidad':mensualidad_revisar,'sopnumbe':sopnumbe,'docdate':docdate,'docid':docid,'custnmbr':custnmbr,'club_id':club.id,'valor_cuota':unitprce,'subtotal':unitprce * cantidad_donaciones_mes,'cantidad_donaciones':cantidad_donaciones_mes,'estado':'Pagada'})

                                        #Como en el objeto de cuotas perdonadas se encuentra la cuota pendiente, y que ahora
                                        #ya no estara pendiente, se pone el campo borrar a True para posteriormente ser 
                                        #borrados todos los registros con el campo borrar = True
                                        cuota_pendiente_id = self.pool.get('sbg.socios_cuotas_perdonadas').search(cr, uid, [('partner_id', '=', cliente.id),('club_id', '=', club.id),('mensualidad', '=', mensualidad_revisar),('estado', '=', 'Pendiente'),('cantidad_donaciones', '=', cantidad_donaciones_mes)])
                                        cuota_pendiente_borrada = False
                                        if cuota_pendiente_id:
                                            self.pool.get('sbg.socios_cuotas_perdonadas').write(cr, uid, cuota_pendiente_id, {'borrar':True})
                                            cuota_pendiente_borrada = True

                                        #Se revisa si el numero de registros ingresados ya es igual al numero de registros
                                        #por ingresar. Si este fuera el caso, hay que tomar en cuenta la posibilidad de que
                                        #este registro sea de un pago incompleto.
                                        registros_ingresados = registros_ingresados + 1
                                        if registros_ingresados == no_registros_ingresar:
                                            buscar_posicion = False
                                            if cuotas_incompletas:
                                                #Si la cuota fue incompleta, se modifica el nuevo registro ingresado al estado
                                                #de cuenta, para que coincida con el numero de cuotas pagadas.
                                                self.pool.get('sbg.socios_estado_de_cuenta').write(cr, uid, nuevo_registro_id, {'subtotal':unitprce * (cantidad_donaciones_mes - cuotas_incompletas),'cantidad_donaciones':cantidad_donaciones_mes - cuotas_incompletas})

                                                #En este caso, hay que agregar un registro con las cuotas pendientes incompletas,
                                                #tanto en el objeto estado de cuenta, como en el de cuotas perdonadas.
                                                if cuota_pendiente_borrada == True:
                                                    self.pool.get("sbg.socios_cuotas_perdonadas").create(cr, uid, {'partner_id':cliente.id,'docdate':docdate,'club_id':club.id,'mensualidad':mensualidad_revisar,'cantidad_donaciones':cuotas_incompletas,'estado':'Pendiente'})

                                    elif cuota_perdonada.cantidad_donaciones < cantidad_donaciones_mes:
                                        nuevo_registro_id = self.pool.get("sbg.socios_estado_de_cuenta").create(cr, uid, {'partner_id':cliente.id,'mensualidad':mensualidad_revisar,'sopnumbe':sopnumbe,'docdate':docdate,'docid':docid,'custnmbr':custnmbr,'club_id':club.id,'valor_cuota':unitprce,'subtotal':unitprce * cantidad_donaciones_mes,'cantidad_donaciones':cantidad_donaciones_mes,'estado':'Pagada'})

                                        registros_ingresados = registros_ingresados + 1
                                        if registros_ingresados == no_registros_ingresar:
                                            buscar_posicion = False
                                            if cuotas_incompletas:
                                                self.pool.get('sbg.socios_estado_de_cuenta').write(cr, uid, nuevo_registro_id, {'subtotal':unitprce * (cantidad_donaciones_mes - cuotas_incompletas),'cantidad_donaciones':cantidad_donaciones_mes - cuotas_incompletas})


                                #Si no existe registro para esta mensualidad en el objeto de cuotas perdonadas, entonces se
                                #puede guardar la cuota pagada sin ningun problema.
                                else:

                                    nuevo_registro_id = self.pool.get("sbg.socios_estado_de_cuenta").create(cr, uid, {'partner_id':cliente.id,'mensualidad':mensualidad_revisar,'sopnumbe':sopnumbe,'docdate':docdate,'docid':docid,'custnmbr':custnmbr,'club_id':club.id,'valor_cuota':unitprce,'subtotal':unitprce * cantidad_donaciones_mes,'cantidad_donaciones':cantidad_donaciones_mes,'estado':'Pagada'})

                                    cuota_pendiente_id = self.pool.get('sbg.socios_cuotas_perdonadas').search(cr, uid, [('partner_id', '=', cliente.id),('club_id', '=', club.id),('mensualidad', '=', mensualidad_revisar),('estado', '=', 'Pendiente')])
                                    if cuota_pendiente_id:
                                        self.pool.get('sbg.socios_cuotas_perdonadas').write(cr, uid, cuota_pendiente_id, {'borrar':True})

                                    registros_ingresados = registros_ingresados + 1

                                    if registros_ingresados == no_registros_ingresar:
                                        buscar_posicion = False
                                        if cuotas_incompletas:
                                            self.pool.get('sbg.socios_estado_de_cuenta').write(cr, uid, nuevo_registro_id, {'subtotal':unitprce * (cantidad_donaciones_mes - cuotas_incompletas),'cantidad_donaciones':cantidad_donaciones_mes - cuotas_incompletas})
                                            if (mensualidad_revisar < mensualidad_actual) or (mensualidad_revisar == mensualidad_actual and int(dia_fecha_inscripcion) < int(dia_actual)):
                                                self.pool.get("sbg.socios_cuotas_perdonadas").create(cr, uid, {'partner_id':cliente.id,'docdate':docdate,'club_id':club.id,'mensualidad':mensualidad_revisar,'cantidad_donaciones':cuotas_incompletas,'estado':'Pendiente'})

                                #Se calcula cual es la nueva mensualidad que se va a verificar si hay espacio para ingresar
                                #el registro en la siguiente repeticion del ciclo. Esto si todavia hay registros por ingresar.
                                mes_mensualidad_tempo = str(mensualidad_revisar)
                                mes_mensualidad = int(mes_mensualidad_tempo[4:7])

                                ano_mensualidad_tempo = str(mensualidad_revisar)
                                ano_mensualidad = int(ano_mensualidad_tempo[0:4])

                                if mes_mensualidad + frecuencia_pagos > 12:
                                    ano_mensualidad = (ano_mensualidad + 1) * 100
                                    mensualidad_revisar = ano_mensualidad + (mes_mensualidad + frecuencia_pagos - 12)
                                else:
                                    mensualidad_revisar = mensualidad_revisar + frecuencia_pagos                            

                    #Finaliza el ciclo de la informacion proveniente de GP. En este momento el objeto estado de cuenta esta
                    #completo con respecto a las cuotas pagadas, pero vacio con respecto a las pendientes y perdonadas.

                    #Se ingresan al objeto estado de cuenta todos los registros perdonados que existen en el objeto de
                    #cuotas perdonadas. Si existieran registros con estado pendiente, tambien se ingresan.
                    cuotas_perdonadas_ids = self.pool.get('sbg.socios_cuotas_perdonadas').search(cr, uid, [('partner_id', '=', cliente.id),('club_id', '=', club.id),('borrar', '=', False)])
                    for cuota_perdonada_id in cuotas_perdonadas_ids:
                        cuota_perdonada = self.pool.get('sbg.socios_cuotas_perdonadas').browse(cr, uid, cuota_perdonada_id)
                        self.pool.get("sbg.socios_estado_de_cuenta").create(cr, uid, {'partner_id':cliente.id,'mensualidad':cuota_perdonada.mensualidad,'docdate':cuota_perdonada.docdate,'club_id':club.id,'cantidad_donaciones':cuota_perdonada.cantidad_donaciones,'estado':cuota_perdonada.estado})

                    #A continuacion se revisara en un ciclo, desde la mensualidad_revisar hasta la mensualidad_actual, cuales
                    #mensualidades estan vacias en el objeto estado de cuenta. Estas mensualidades vacias son las que 
                    #deberian tener estado pendiente, por lo que se hace este proceso.
                    mensualidad_revisar = mensualidad_verificar

                    while mensualidad_revisar <= mensualidad_actual:

                        factura_id = self.pool.get('sbg.socios_estado_de_cuenta').search(cr, uid, [('partner_id', '=', cliente.id),('club_id', '=', club.id),('mensualidad', '=', mensualidad_revisar)])
                        #Si existe registro, se calcula la siguiente mensualidad para el ciclo.
                        if factura_id:

                            mes_mensualidad_tempo = str(mensualidad_revisar)
                            mes_mensualidad = int(mes_mensualidad_tempo[4:7])
                            mes_mensualidad_texto = mes_mensualidad_tempo[4:7]

                            ano_mensualidad_tempo = str(mensualidad_revisar)
                            ano_mensualidad = int(ano_mensualidad_tempo[0:4])

                            docdate = str(ano_mensualidad) + '-' + str(mes_mensualidad_texto) + '-31'

                            socio_club_configuracion_ids = self.pool.get('sbg.socios_clubs_configuracion').search(cr, uid, [('partner_id', '=', cliente.id),('socio_clubs_id', '=', socio_club_id)],order='fecha_configuracion desc')
                            for socio_club_configuracion_id in socio_club_configuracion_ids:
                                socio_club_configuracion = self.pool.get('sbg.socios_clubs_configuracion').browse(cr, uid, socio_club_configuracion_id)

                                if docdate >= socio_club_configuracion.fecha_configuracion:
                                    frecuencia_pagos = 12 / int(socio_club_configuracion.cantidad_pagos_anual)

                            if mes_mensualidad + frecuencia_pagos > 12:
                                ano_mensualidad = (ano_mensualidad + 1) * 100
                                mensualidad_revisar = ano_mensualidad + (mes_mensualidad + frecuencia_pagos - 12)
                            else:
                                mensualidad_revisar = mensualidad_revisar + frecuencia_pagos

                        #Si no existe factura, se ingresa un registro con estado pendiente en dicha mensualidad en el objeto
                        #estado de cuenta, y se revisa el objeto de cuotas perdonadas para ingresar dicho registro tambien.
                        else:
                            if (mensualidad_revisar < mensualidad_actual) or (mensualidad_revisar == mensualidad_actual and int(dia_fecha_inscripcion) < int(dia_actual)):

                                mes_mensualidad_tempo = str(mensualidad_revisar)
                                mes_mensualidad = int(mes_mensualidad_tempo[4:7])

                                ano_mensualidad_tempo = str(mensualidad_revisar)
                                ano_mensualidad = int(ano_mensualidad_tempo[0:4])

                                docdate = str(ano_mensualidad) + '-' + mes_mensualidad_tempo[4:7] + '-31'

                                cantidad_donaciones_mes = 0
                                socio_club_configuracion_ids = self.pool.get('sbg.socios_clubs_configuracion').search(cr, uid, [('partner_id', '=', cliente.id),('socio_clubs_id', '=', socio_club_id)],order='fecha_configuracion desc')

                                for socio_club_configuracion_id in socio_club_configuracion_ids:
                                    socio_club_configuracion = self.pool.get('sbg.socios_clubs_configuracion').browse(cr, uid, socio_club_configuracion_id)

                                    if docdate >= socio_club_configuracion.fecha_configuracion:
                                        frecuencia_pagos = 12 / int(socio_club_configuracion.cantidad_pagos_anual)
                                        cantidad_donaciones_mes = socio_club_configuracion.cantidad_donaciones_mes


                                fecha_pendiente = str(mensualidad_revisar)

                                if fecha_pendiente[4:7] == '02' and int(dia_fecha_inscripcion) > 28:
                                    dia_pendiente = '28'
                                elif fecha_pendiente[4:7] == '04' and int(dia_fecha_inscripcion) > 30:
                                    dia_pendiente = '30'
                                elif fecha_pendiente[4:7] == '06' and int(dia_fecha_inscripcion) > 30:
                                    dia_pendiente = '30'
                                elif fecha_pendiente[4:7] == '09' and int(dia_fecha_inscripcion) > 30:
                                    dia_pendiente = '30'
                                elif fecha_pendiente[4:7] == '11' and int(dia_fecha_inscripcion) > 30:
                                    dia_pendiente = '30'
                                else:
                                    dia_pendiente = dia_fecha_inscripcion

                                fecha_pendiente = fecha_pendiente[0:4] + '-' + fecha_pendiente[4:7] + '-' + str(dia_pendiente)

                                self.pool.get("sbg.socios_estado_de_cuenta").create(cr, uid, {'partner_id':cliente.id,'docdate':fecha_pendiente,'club_id':club.id,'mensualidad':mensualidad_revisar,'cantidad_donaciones':cantidad_donaciones_mes,'estado':'Pendiente'})
                                cuota_pendiente_id = self.pool.get('sbg.socios_cuotas_perdonadas').search(cr, uid, [('partner_id', '=', cliente.id),('club_id', '=', club.id),('mensualidad', '=', mensualidad_revisar)])
                                if not cuota_pendiente_id:
                                    self.pool.get("sbg.socios_cuotas_perdonadas").create(cr, uid, {'partner_id':cliente.id,'docdate':fecha_pendiente,'club_id':club.id,'mensualidad':mensualidad_revisar,'cantidad_donaciones':cantidad_donaciones_mes,'estado':'Pendiente'})
                            else:
                                mensualidad_revisar = mensualidad_actual + 1

                    #Los registros que han sido modificados a borrar = True en el objeto de cuotas pagadas, son borrados.
                    cuotas_pendientes_ids = self.pool.get('sbg.socios_cuotas_perdonadas').search(cr, uid, [('partner_id', '=', cliente.id),('borrar', '=', True)])
                    self.pool.get('sbg.socios_cuotas_perdonadas').unlink(cr, uid, cuotas_pendientes_ids)

            result[cliente.id] = "1"

        return result

    def _socios_obtener_estado_de_cuenta(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for id in ids:
            facturas_ids = self.pool.get('sbg.socios_estado_de_cuenta').search(cr, uid, [('partner_id', '=', id)], offset=0, limit=None)

            result[id] = facturas_ids

        return result

    def onchange_tarifas(self, cr, uid, ids, tarifa):

        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=None)
        for group in current_user.groups_id:
            if group.name == "SBG - Tarifas con restriccion":
                if tarifa not in (1,3,4):
                    return {'value': {'property_product_pricelist': ''}}
                else:
                    return {'value': {'property_product_pricelist': tarifa}}
            if group.name == "SBG - Todas las tarifas":
                return {}
        if tarifa != 1:
            return {'value': {'property_product_pricelist': ''}}
        else:
            return {'value': {'property_product_pricelist': tarifa}}


    def _obtener_ref_id(self, cr, uid, context=None):

        secuencia_ids = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'Clientes - Ref')])
        secuencia_id = self.pool.get('ir.sequence').browse(cr, uid, secuencia_ids)[0]
        secuencia = self.pool.get('ir.sequence').get_id(cr, uid, secuencia_id.id)

        return secuencia

    def name_get(self, cr, user, ids, context={}):

        res = super(res_partner, self).name_get(cr, user, ids, context)
        new_res = []

        for partner_id, partner_name in res:
        
            partner = self.pool.get('res.partner').browse(cr, user, partner_id)

            if partner.ref is not False and partner.ref != '':
                partner_name = partner_name + ' - ' + partner.ref

            new_res.append((partner_id, partner_name))

        return new_res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args=[]
        if not context:
            context={}
        if name:
            ids = self.search(cr, uid, [('ref', '=', name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('vat', operator, name)] + args, limit=limit, context=context)
            if not ids:
                ids = self.search(cr, uid, [('name', operator, name)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

    def _region(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for cliente in self.pool.get('res.partner').browse(cr, uid, ids):

            if cliente.municipio_id:
                result[cliente.id] = cliente.municipio_id.region_id.id

        return result

    def _departamento(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for cliente in self.pool.get('res.partner').browse(cr, uid, ids):

            if cliente.municipio_id:
                result[cliente.id] = cliente.municipio_id.departamento_id.id

        return result

    _columns = {
        'promotor': fields.char('Promotor', size=40),
        'clase_de_cliente': fields.char('Clase de Cliente', size=40),
        'como_nos_conocio_id': fields.many2one('sbg.como_nos_conocio', 'Como nos conocio'),
        'sexo': fields.selection([('Femenino','Femenino'),('Masculino','Masculino')], 'Genero'),
        'fecha_inscripcion': fields.date('Fecha de Inscripcion'),
        'empresa_donde_trabaja': fields.char('Empresa donde trabaja', size=40),
        'direccion_donde_trabaja': fields.char('Direccion donde trabaja', size=80),
        'telefono_donde_trabaja': fields.char('Telefono donde trabaja', size=20),        
        'puesto_desempena_id': fields.many2one('sbg.puesto_desempena', 'Puesto que desempena'),
        'horario_llamar_desde': fields.selection([('0:00','0:00 a.m.'),('0:30','0:30 a.m.'),('1:00','1:00 a.m.'),('1:30','1:30 a.m.'),('2:00','2:00 a.m.'),('2:30','2:30 a.m.'),('33:00','3:00 a.m.'),('3:30','3:30 a.m.'),('4:00','4:00 a.m.'),('4:30','4:30 a.m.'),('5:00','5:00 a.m.'),('5:30','5:30 a.m.'),('6:00','6:00 a.m.'),('6:30','6:30 a.m.'),('7:00','7:00 a.m.'),('7:30','7:30 a.m.'),('8:00','8:00 a.m.'),('8:30','8:30 a.m.'),('9:00','9:00 a.m.'),('9:30','9:30 a.m.'),('10:00','10:00 a.m.'),('10:30','10:30 a.m.'),('11:00','11:00 a.m.'),('11:30','11:30 a.m.'),('12:00','12:00 p.m.'),('12:30','12:30 p.m.'),('13:00','13:00 p.m.'),('13:30','13:30 p.m.'),('14:00','14:00 p.m.'),('14:30','14:30 p.m.'),('15:00','15:00 p.m.'),('15:30','15:30 p.m.'),('16:00','16:00 p.m.'),('16:30','16:30 p.m.'),('17:00','17:00 p.m.'),('17:30','17:30 p.m.'),('18:00','18:00 p.m.'),('18:30','18:30 p.m.'),('19:00','19:00 p.m.'),('19:30','19:30 p.m.'),('20:00','20:00 p.m.'),('20:30','20:30 p.m.'),('21:00','21:00 p.m.'),('21:30','21:30 p.m.'),('22:00','22:00 p.m.'),('22:30','22:30 p.m.'),('23:00','23:00 p.m.'),('23:30','23:30 p.m.')], 'Llamar desde (Hora)'),
        'horario_llamar_hasta': fields.selection([('0:00','0:00 a.m.'),('0:30','0:30 a.m.'),('1:00','1:00 a.m.'),('1:30','1:30 a.m.'),('2:00','2:00 a.m.'),('2:30','2:30 a.m.'),('33:00','3:00 a.m.'),('3:30','3:30 a.m.'),('4:00','4:00 a.m.'),('4:30','4:30 a.m.'),('5:00','5:00 a.m.'),('5:30','5:30 a.m.'),('6:00','6:00 a.m.'),('6:30','6:30 a.m.'),('7:00','7:00 a.m.'),('7:30','7:30 a.m.'),('8:00','8:00 a.m.'),('8:30','8:30 a.m.'),('9:00','9:00 a.m.'),('9:30','9:30 a.m.'),('10:00','10:00 a.m.'),('10:30','10:30 a.m.'),('11:00','11:00 a.m.'),('11:30','11:30 a.m.'),('12:00','12:00 p.m.'),('12:30','12:30 p.m.'),('13:00','13:00 p.m.'),('13:30','13:30 p.m.'),('14:00','14:00 p.m.'),('14:30','14:30 p.m.'),('15:00','15:00 p.m.'),('15:30','15:30 p.m.'),('16:00','16:00 p.m.'),('16:30','16:30 p.m.'),('17:00','17:00 p.m.'),('17:30','17:30 p.m.'),('18:00','18:00 p.m.'),('18:30','18:30 p.m.'),('19:00','19:00 p.m.'),('19:30','19:30 p.m.'),('20:00','20:00 p.m.'),('20:30','20:30 p.m.'),('21:00','21:00 p.m.'),('21:30','21:30 p.m.'),('22:00','22:00 p.m.'),('22:30','22:30 p.m.'),('23:00','23:00 p.m.'),('23:30','23:30 p.m.')], 'Llamar hasta (Hora)'),
        'dias_visita_id': fields.many2many('sbg.dias_semana', 'res_partner_dias_semana_rel', 'partner_id', 'dias_semana_id', 'Dias de la semana'),
        'profesion_id': fields.many2one('sbg.profesion', 'Profesion'),
        'religion_id': fields.many2one('sbg.religion', 'Religion'),
        'estado_civil_id': fields.many2one('sbg.estado_civil', 'Estado Civil'),
        'numero_hijos': fields.integer('Numero de hijos'),
        'nombre_conyuge': fields.char('Nombre del Conyuge', size=40),
        'fecha_nacimiento': fields.date('Fecha de Nacimiento', size=10),
        'fecha_casamiento': fields.date('Fecha de Casamiento', size=10),
        'nombre_iglesia_asiste': fields.char('Nombre iglesia donde asiste', size=40),
        'denominacion_iglesia_id': fields.many2one('sbg.denominacion_iglesia', 'Denominacion de la iglesia'),
        'representante_oficial_iglesia': fields.char('Nombre del representante de la iglesia', size=40),
        'direccion_iglesia': fields.char('Direccion de la iglesia', size=100),
        'telefono_iglesia': fields.char('Telefono de la iglesia', size=30),
        'codigo_metodo_envio_id': fields.many2one('sbg.codigo_metodo_envio', 'Codigo del metodo de envio'),
        'direccion_donde_recibe': fields.char('Direccion donde recibe', size=100),
        'horario_visita_desde': fields.selection([('0:00','0:00 a.m.'),('0:30','0:30 a.m.'),('1:00','1:00 a.m.'),('1:30','1:30 a.m.'),('2:00','2:00 a.m.'),('2:30','2:30 a.m.'),('33:00','3:00 a.m.'),('3:30','3:30 a.m.'),('4:00','4:00 a.m.'),('4:30','4:30 a.m.'),('5:00','5:00 a.m.'),('5:30','5:30 a.m.'),('6:00','6:00 a.m.'),('6:30','6:30 a.m.'),('7:00','7:00 a.m.'),('7:30','7:30 a.m.'),('8:00','8:00 a.m.'),('8:30','8:30 a.m.'),('9:00','9:00 a.m.'),('9:30','9:30 a.m.'),('10:00','10:00 a.m.'),('10:30','10:30 a.m.'),('11:00','11:00 a.m.'),('11:30','11:30 a.m.'),('12:00','12:00 p.m.'),('12:30','12:30 p.m.'),('13:00','13:00 p.m.'),('13:30','13:30 p.m.'),('14:00','14:00 p.m.'),('14:30','14:30 p.m.'),('15:00','15:00 p.m.'),('15:30','15:30 p.m.'),('16:00','16:00 p.m.'),('16:30','16:30 p.m.'),('17:00','17:00 p.m.'),('17:30','17:30 p.m.'),('18:00','18:00 p.m.'),('18:30','18:30 p.m.'),('19:00','19:00 p.m.'),('19:30','19:30 p.m.'),('20:00','20:00 p.m.'),('20:30','20:30 p.m.'),('21:00','21:00 p.m.'),('21:30','21:30 p.m.'),('22:00','22:00 p.m.'),('22:30','22:30 p.m.'),('23:00','23:00 p.m.'),('23:30','23:30 p.m.')], 'Visita desde (Hora)'),
        'horario_visita_hasta': fields.selection([('0:00','0:00 a.m.'),('0:30','0:30 a.m.'),('1:00','1:00 a.m.'),('1:30','1:30 a.m.'),('2:00','2:00 a.m.'),('2:30','2:30 a.m.'),('33:00','3:00 a.m.'),('3:30','3:30 a.m.'),('4:00','4:00 a.m.'),('4:30','4:30 a.m.'),('5:00','5:00 a.m.'),('5:30','5:30 a.m.'),('6:00','6:00 a.m.'),('6:30','6:30 a.m.'),('7:00','7:00 a.m.'),('7:30','7:30 a.m.'),('8:00','8:00 a.m.'),('8:30','8:30 a.m.'),('9:00','9:00 a.m.'),('9:30','9:30 a.m.'),('10:00','10:00 a.m.'),('10:30','10:30 a.m.'),('11:00','11:00 a.m.'),('11:30','11:30 a.m.'),('12:00','12:00 p.m.'),('12:30','12:30 p.m.'),('13:00','13:00 p.m.'),('13:30','13:30 p.m.'),('14:00','14:00 p.m.'),('14:30','14:30 p.m.'),('15:00','15:00 p.m.'),('15:30','15:30 p.m.'),('16:00','16:00 p.m.'),('16:30','16:30 p.m.'),('17:00','17:00 p.m.'),('17:30','17:30 p.m.'),('18:00','18:00 p.m.'),('18:30','18:30 p.m.'),('19:00','19:00 p.m.'),('19:30','19:30 p.m.'),('20:00','20:00 p.m.'),('20:30','20:30 p.m.'),('21:00','21:00 p.m.'),('21:30','21:30 p.m.'),('22:00','22:00 p.m.'),('22:30','22:30 p.m.'),('23:00','23:00 p.m.'),('23:30','23:30 p.m.')], 'Visita hasta (Hora)'),
        'nombre_transporte_id': fields.many2one('sbg.transporte', 'Nombre del transporte'),
        'direccion_transporte': fields.char('Direccion del transporte', size=100),
        'telefono_transporte': fields.char('Telefono del transporte', size=30),
        'diosesis_id': fields.many2one('sbg.diosesis', 'Jerarquias Eclesiasticas'),
        'parroquia': fields.char('Parroquia', size=40),
        'parroco': fields.char('Parroco', size=40),
        'correo_electronico': fields.char('Correo electronico', size=200),
        'clubs': fields.one2many('sbg.socios_clubs', 'partner_id', 'Clubs'),
        #'crear_estado_de_cuenta': fields.function(_socios_crear_estado_de_cuenta, type='char', method=True, string='Estado de Cuenta'),
        'estado_de_cuenta': fields.function(_socios_obtener_estado_de_cuenta, type='one2many', obj="sbg.socios_estado_de_cuenta", method=True, string='Estado de Cuenta'),
        'cuotas_perdonadas': fields.one2many('sbg.socios_cuotas_perdonadas', 'partner_id', 'Cuotas Perdonadas'),
        'municipio_id': fields.many2one('sbg.municipios', 'Municipio'),
        'region_id': fields.function(_region, type='many2one', obj="sbg.regiones", method=True, string='Region'),
        'departamento_id': fields.function(_departamento, type='many2one', obj="sbg.departamentos", method=True, string='Departamento'),
        'estado_o_provincia': fields.char('Estado o Provincia', size=50),
    }
    _defaults = {
        'ref': _obtener_ref_id,
    }
res_partner()

#class res_partner_address(osv.osv):
#    _inherit = 'res.partner.address'
#    _columns = {
#        'estado_o_provincia': fields.char('Estado o Provincia', size=50)
#    }
#res_partner_address()
