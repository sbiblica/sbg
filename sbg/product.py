# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp


def check_ean_sbg(eancode):
    return True


class product_product(osv.osv):
    _inherit = 'product.product'

    def _check_ean_key(self, cr, uid, ids, context=None):
        for product in self.browse(cr, uid, ids, context=context):
            res = check_ean_sbg(product.ean13)
        return res


    def _tarifa_a(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'A')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result

    def _tarifa_b(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'B')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result

    def _tarifa_c(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'C')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result

    def _tarifa_d(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'D')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result

    def _tarifa_e(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'E')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result

    def _tarifa_ee(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'EE')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result

    def _tarifa_eee(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'EEE')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result

    def _tarifa_minimo(self, cr, uid, ids, field_name, arg, context):
        result = {}

        pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '=', 'MINIMO')])[0]

        for producto in self.browse(cr, uid, ids):
            result[producto.id] = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist_ids], producto.id, 1)[pricelist_ids]
        return result


    _columns = {
        'tarifa_a': fields.function(_tarifa_a, type='float', method=True, string='A', digits_compute= dp.get_precision('Product Price')),
        'tarifa_b': fields.function(_tarifa_b, type='float', method=True, string='B', digits_compute= dp.get_precision('Product Price')),
        'tarifa_c': fields.function(_tarifa_c, type='float', method=True, string='C', digits_compute= dp.get_precision('Product Price')),
        'tarifa_d': fields.function(_tarifa_d, type='float', method=True, string='D', digits_compute= dp.get_precision('Product Price')),
        'tarifa_e': fields.function(_tarifa_e, type='float', method=True, string='E', digits_compute= dp.get_precision('Product Price')),
        'tarifa_ee': fields.function(_tarifa_ee, type='float', method=True, string='EE', digits_compute= dp.get_precision('Product Price')),
        'tarifa_eee': fields.function(_tarifa_eee, type='float', method=True, string='EEE', digits_compute= dp.get_precision('Product Price')),
        'tarifa_minimo': fields.function(_tarifa_minimo, type='float', method=True, string='Minimos', digits_compute= dp.get_precision('Product Price')),
    }

    _constraints = [(_check_ean_key, 'Error: Invalid ean code', ['ean13'])]

product_product()

