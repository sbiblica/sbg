# -*- coding: utf-8 -*-
from openerp import tools
from openerp.osv import fields, osv

class sbg_sales(osv.osv):
    _name = 'sbg.sales'
    _description = 'SBG Sales'
    _auto = False

    _columns = {
        'reference': fields.char('Reference'),
        'date_order': fields.datetime(string="Order date"),
        'partner_id': fields.many2one('res.partner', 'Customer' , readonly=True),
        'customer_city': fields.char('Customer city'),
        'customer_type': fields.char('Customer type'),
        'promoter': fields.char('Promoter'),
        'location_id': fields.many2one('stock.location', 'Location' , readonly=True),
        'product_id': fields.many2one('product.product', 'Product' , readonly=True),
        'qty': fields.float(string='Quantity'),
        'price_unit': fields.float(string='Unit price'),
        'line_amount': fields.float(string='Line amount')
    }
    _order = 'date_order desc'

    def init(self, cr, uid=1):
        tools.drop_view_if_exists(cr, self._table)
        cr.execute("""
            CREATE OR REPLACE VIEW %s AS (
                SELECT ol.id, o.name as reference, o.date_order, o.partner_id, COALESCE(p.city, '') as customer_city, COALESCE(p.clase_de_cliente, '') as customer_type,
                COALESCE(p.promotor, '') as promoter, w.view_location_id as location_id,
                ol.product_id, COALESCE(ol.product_uom_qty, 0) AS qty, COALESCE(ol.discount, 0) AS discount,
                ROUND(COALESCE(ol.price_unit, 0) / (1 + COALESCE(a.amount, 0)), 2) AS price_unit,
                ROUND(COALESCE(ol.product_uom_qty, 0) * COALESCE(ol.price_unit / (1 + COALESCE(a.amount, 0)), 0) - COALESCE(ol.discount, 0), 2) AS line_amount
                FROM sale_order o
                LEFT JOIN res_partner p
                ON p.id = o.partner_id
                LEFT JOIN stock_warehouse w
                ON w.id = o.warehouse_id
                LEFT JOIN sale_order_line ol
                ON ol.order_id = o.id
                LEFT JOIN product_product pp
                ON pp.id = ol.product_id
                LEFT JOIN product_taxes_rel ptr
                ON ptr.prod_id = pp.product_tmpl_id
                LEFT JOIN account_tax a
                ON a.id = ptr.tax_id
                WHERE o.state not in ('draft', 'cancel')
                UNION
                SELECT ol.id, o.name as reference, o.date_order, o.partner_id, COALESCE(p.city, '') as customer_city, COALESCE(p.clase_de_cliente, '') as customer_type,
                COALESCE(p.promotor, '') as promoter, o.location_id,
                ol.product_id, COALESCE(ol.qty, 0) AS qty, COALESCE(ol.discount, 0) AS discount,
                ROUND(COALESCE(ol.price_unit, 0) / (1 + COALESCE(a.amount, 0)), 2) AS price_unit,
                ROUND(COALESCE(ol.qty, 0) * COALESCE(ol.price_unit / (1 + COALESCE(a.amount, 0)), 0) - COALESCE(ol.discount, 0), 2) AS line_amount
                FROM pos_order o
                LEFT JOIN res_partner p
                ON p.id = o.partner_id
                LEFT JOIN pos_order_line ol
                ON ol.order_id = o.id
                LEFT JOIN product_product pp
                ON pp.id = ol.product_id
                LEFT JOIN product_taxes_rel ptr
                ON ptr.prod_id = pp.product_tmpl_id
                LEFT JOIN account_tax a
                ON a.id = ptr.tax_id
                WHERE o.state in ('invoiced')
            )
        """ % (self._table))
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
