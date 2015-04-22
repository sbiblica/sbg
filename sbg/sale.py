# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import time
import logging

class sale_order(osv.osv):

    _name = 'sale.order'
    _inherit = 'sale.order'

    _columns = {
        'add_disc':fields.float('Additional Discount(%)',digits=(4,2), readonly=True, states={'draft': [('readonly', False)]}),
        'producto_descuento': fields.many2one('product.product', 'Descuento', domain=[('sale_ok', '=', True)]),
        'journal_id': fields.many2one('account.journal', 'Diario', required=True, readonly=True, states={'draft':[('readonly',False)]}),
        'cotizacion':fields.boolean('Cotizacion'),
    }

    _defaults={
        'add_disc': 0.0,
    }

    def validar_inventario(self, cr, uid, product_id, qty, context=None):
        producto = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
        logging.warn(producto.virtual_available)

        if producto.type=='product':

            if producto.virtual_available < qty:
                return producto

        elif producto.type=='consu':

            boms = self.pool.get('mrp.bom').search(cr, uid, [('type','=','phantom'), ('product_tmpl_id','=',producto.product_tmpl_id.id)], context=context)
            for b in self.pool.get('mrp.bom').browse(cr, uid, boms, context=context):

                for l in b.bom_line_ids:

                    sub_producto = self.pool.get('product.product').browse(cr, uid, l.product_id.id, context=context)
                    if sub_producto.virtual_available < l.product_qty * qty:
                        return sub_producto

        return None

    def descuento_adicional(self, cr, uid, ids, *args):
        """ Agrega un descuento al total
        @return: True
        """
        if not len(ids):
            return False

        for order in self.browse(cr, uid, ids):

            for l in order.order_line:
                if l.price_subtotal < 0:
                    raise osv.except_osv('Error', 'Ya se ha hecho un descuento')

            if not order.producto_descuento:
                raise osv.except_osv('Error', 'Debe escoger un descuento')

            total = order.amount_total * order.add_disc * 0.01

            impuestos = []
            for tax_id in order.producto_descuento.taxes_id:
                impuestos.append((4,tax_id.id))

            self.pool.get('sale.order.line').create(cr, uid, {
                'name':order.producto_descuento.name,
                'company_id': order.company_id.id,
                'product_id': order.producto_descuento.id,
                'price_unit': -total,
                'product_uom_qty': 1,
                'product_uom': order.producto_descuento.uom_id.id,
                'order_id': order.id,
                'sequence': 9999,
                'tax_id': impuestos,
            })

        return True

    def action_wait(self, cr, uid, ids, context=None):
        super(sale_order, self).action_wait(cr, uid, ids, context)

        for order in self.browse(cr, uid, ids):
            context = context or {}
            ctx = {}
            ctx.update({'warehouse': order.warehouse_id.id})

            for l in order.order_line:
                producto = self.validar_inventario(cr, uid, l.product_id.id, l.product_uom_qty, context=ctx)
                if producto:
                    raise osv.except_osv(_('Not enough stock !'), _('You plan to sell %.2f but you only have %.2f available !') % (l.product_uom_qty, producto.virtual_available))
        return True

    def limite_credito(self, cr, uid, ids):
        for order in self.browse(cr, uid, ids):
            if order.journal_id.punto_de_venta == True:
                return True
            limite_credito = order.partner_id.credit_limit
            credito_actual = order.partner_id.credit
        if (limite_credito - credito_actual - order.amount_total) < 0:
            raise osv.except_osv('Cliente rebasó crédito autorizado', 'Favor pedir autorización para poder facturar')
            return False
        else:
            return True

sale_order()


class sbg_sale_order_line(osv.osv):
    _inherit = 'sale.order.line'

    def _precio_unidad(self, cursor, user, ids, name, arg, context=None):
        res = {}
        for line in self.browse(cursor, user, ids, context=context):
            res[line.id] = line.price_unit
        return res

    def _acceso_precio_descuento(self, cr, uid, context=None):
        current_user = self.pool.get('res.users').browse(cr, uid, uid, context)
        for group in current_user.groups_id:
            if group.name == "SBG - Modificar precio y descuento":
                return True
        return False

    _columns = {
        'price_unit2': fields.function(_precio_unidad, method=True, string='Precio unidad', type='float'),
        'acceso_precio_descuento': fields.boolean("bandera modificar precio y descuento"),
    }
    _defaults = {
        'acceso_precio_descuento': _acceso_precio_descuento,
    }

    def product_id_change_with_wh(self, cr, uid, ids, pricelist, product, qty=0, uom=False, qty_uos=0, uos=False, name='', partner_id=False, lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, warehouse_id=False, context=None):

        res =  super(sbg_sale_order_line, self).product_id_change_with_wh(cr, uid, ids, pricelist, product, qty=qty, uom=False, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id, lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, warehouse_id=warehouse_id, context=context)

        l = self.browse(cr, uid, ids, context=context)
        if l.order_id.cotizacion == False:
            context = context or {}
            ctx = context.copy()
            ctx.update({'warehouse': warehouse_id})

            producto = self.pool.get('sale.order').validar_inventario(cr, uid, product, qty, context=ctx)
            logging.warn(producto)
            if producto:
                res['warning'] = {'title':_('Not enough stock !'), 'message': _('You plan to sell %.2f but you only have %.2f available !') % (qty, producto.virtual_available)}
                res['value'].update({'product_uom_qty': 0})

        return res

sbg_sale_order_line()
