# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import datetime
import time
import openerp.addons.decimal_precision as dp

class sbg_diferencias_inventario(osv.osv):
    _name = 'sbg.diferencias.inventario'

    def generar_diferencias(self, cr, uid, ids, context={}):

        for inventario in self.pool.get('sbg.diferencias.inventario').browse(cr, uid, ids):

            id = inventario.inventario_id.id

            cr.execute("SELECT pc.id, count(*) FROM product_category pc, product_product pp, stock_inventory_line sil, product_template pt WHERE sil.product_id = pp.id AND pp.product_tmpl_id = pt.id AND pt.categ_id = pc.id AND sil.inventory_id = " + str(id) + " GROUP BY pc.id ORDER BY pc.id")

            for row_categ in cr.fetchall():
                categ_id = row_categ[0]
                categ_count = row_categ[1]

                costo_total_categoria = 0

                if inventario.ubicacion_id.id:
                    lineas_ids = self.pool.get('stock.inventory.line').search(cr, uid, [('inventory_id', '=', id), ('product_id.product_tmpl_id.categ_id', '=', categ_id), ('location_id', '=' ,inventario.ubicacion_id.id)])
                else:
                    lineas_ids = self.pool.get('stock.inventory.line').search(cr, uid, [('inventory_id', '=', id), ('product_id.product_tmpl_id.categ_id', '=', categ_id)])


                for linea_id in lineas_ids:

                    linea = self.pool.get('stock.inventory.line').browse(cr, uid, linea_id)

                    cr.execute("SELECT sm.location_id, sm.product_qty FROM stock_move sm, stock_inventory_move_rel simr WHERE sm.id = simr.move_id AND simr.inventory_id = " + str(id) + " AND sm.product_id = " + str(linea.product_id.id) + " and (sm.location_dest_id = " + str(linea.location_id.id) + " or sm.location_id = " + str(linea.location_id.id) + ")")

                    lineas_diferencias = cr.fetchall()

                    if len(lineas_diferencias) > 0:
                        for row_move in lineas_diferencias:
                            move_location_id = row_move[0]
                            move_product_qty = row_move[1]
                            
                            if move_location_id == 5: #Perdidas de inventario
                                cantidad_sistema = linea.product_qty - move_product_qty
                                diferencia_cantidad = move_product_qty
                            else:
                                cantidad_sistema = linea.product_qty + move_product_qty
                                diferencia_cantidad = -move_product_qty

                            costo_ids = self.pool.get('product.historic.cost').search(cr, uid, [('product_id', '=', linea.product_id.id),('name', '<=', '2012-06-30')],limit=1,order='name desc')

                            if len(costo_ids) > 0:
                                for costo_id in costo_ids:
                                    costo = self.pool.get('product.historic.cost').browse(cr, uid, costo_id)

                                    #costo_real = costo['price'] * linea.product_qty
                                    #costo_diferencia = costo['price'] * diferencia_cantidad
                                    #costo_total_categoria = costo_total_categoria + costo_real - costo_diferencia
                                    costo_real = linea.product_id.standard_price * linea.product_qty
                                    costo_diferencia = linea.product_id.standard_price * diferencia_cantidad
                                    costo_total_categoria = costo_total_categoria + costo_real - costo_diferencia

                                    self.pool.get('sbg.diferencias.inventario.lineas').create(cr, uid, {'diferencias_id':inventario.id, 'product_id':linea.product_id.id, 'cantidad_sistema':cantidad_sistema, 'cantidad_real':linea.product_qty, 'costo':costo_real, 'diferencia_cantidad':diferencia_cantidad, 'diferencia_costo': costo_diferencia, 'total_categoria':'0'})
                            else:
                                self.pool.get('sbg.diferencias.inventario.lineas').create(cr, uid, {'diferencias_id':inventario.id, 'product_id':linea.product_id.id, 'cantidad_sistema':cantidad_sistema, 'cantidad_real':linea.product_qty, 'costo':linea.product_id.standard_price * linea.product_qty, 'diferencia_cantidad':diferencia_cantidad, 'diferencia_costo': 0, 'total_categoria':'0'})
                    else:
                        self.pool.get('sbg.diferencias.inventario.lineas').create(cr, uid, {'diferencias_id':inventario.id, 'product_id':linea.product_id.id, 'cantidad_sistema':linea.product_qty, 'cantidad_real':linea.product_qty, 'costo':linea.product_id.standard_price * linea.product_qty, 'diferencia_cantidad':0, 'diferencia_costo': 0, 'total_categoria':'0'})
                            
        return True

    _columns = {
        'name': fields.char('Nombre', size=40, required=True),
        'inventario_id': fields.many2one('stock.inventory', 'Inventario', required=True),
        'ubicacion_id': fields.many2one('stock.location', 'Ubicacion'),
        'diferencias': fields.one2many('sbg.diferencias.inventario.lineas', 'diferencias_id', 'Diferencias'),
#        'diferencias2': fields.function(_generar_diferencias2, type='char', method=True, string='Diferencias2'),
    }
sbg_diferencias_inventario()


class sbg_diferencias_inventario_lineas(osv.osv):
    _name = 'sbg.diferencias.inventario.lineas'
    _rec_name = 'product_id'


    def _categoria(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for linea in self.pool.get('sbg.diferencias.inventario.lineas').browse(cr, uid, ids):

            result[linea.id] = linea.product_id.product_tmpl_id.categ_id.name

        return result

    _columns = {
        'diferencias_id': fields.many2one('sbg.diferencias.inventario', 'Inventario', ondelete='cascade'),
        'product_id': fields.many2one('product.product', 'Producto'),
        'cantidad_sistema': fields.float('Cantidad sistema', digits_compute=dp.get_precision('Product UoM')),
        'cantidad_real': fields.float('Cantidad real', digits_compute=dp.get_precision('Product UoM')),
        'costo': fields.float('Costo', digits_compute=dp.get_precision('Account')),
        'diferencia_cantidad': fields.float('Diferencia cantidad', digits_compute=dp.get_precision('Product UoM')),
        'diferencia_costo': fields.float('Diferencia costo', digits_compute=dp.get_precision('Account')),
        'categoria': fields.function(_categoria, type='char', method=True, string='Categoria Producto'),
        'total_categoria': fields.char('Total por categoria', size=40),
    }
sbg_diferencias_inventario_lineas()
