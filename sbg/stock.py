# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import logging

class stock_picking(osv.osv):
    _inherit = 'stock.picking'

    def action_pedido_venta(self, cr, uid, ids, context=None):

        for obj in self.browse(cr, uid, ids, context):

            vals = {
                'origin': obj.name,
                'partner_id': obj.partner_id.id,
                'pricelist_id': obj.partner_id.property_product_pricelist.id,
                'partner_invoice_id': obj.partner_id.id,
                'partner_shipping_id': obj.partner_id.id,
                'journal_id': 10,
            }

            orden_id = self.pool.get("sale.order").create(cr, uid, vals, context)

            for linea in obj.move_lines:

                product_info = self.pool.get("sale.order.line").product_id_change(cr, uid, ids, obj.partner_id.property_product_pricelist.id, linea.product_id.id, linea.product_qty,False, 0, False, '', obj.partner_id.id,False, True, False, False, False, False, context)
                if product_info['warning']:
                    raise osv.except_osv(product_info['warning']['title'], product_info['warning']['message'])

                tax_array = []

                for tax in product_info['value']['tax_id']:
                    tax_array.append((4, tax))

                line_vals = {
                    'order_id': orden_id,
                    'name': linea.product_id.name,
                    'price_unit': product_info['value']['price_unit'],
                    'product_uom_qty': linea.product_qty,
                    'product_uom': product_info['value']['product_uom'],
                    'product_uos_qty': product_info['value']['product_uos_qty'],
                    'name': product_info['value']['name'],
                    'product_id': linea.product_id.id,
                    'tax_id': tax_array,
                }
                linea_id = self.pool.get("sale.order.line").create(cr, uid, line_vals, context)

        return True

# class stock_move(osv.osv):
#     _inherit = 'stock.move'
#
#     _columns = {
#         'analytic_id': fields.many2one('account.analytic.account', 'Cuenta analitica', readonly=True, states={'draft':[('readonly',False)]}),
#     }
