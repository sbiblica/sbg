# -*- coding: utf-8 -*-

from openerp.osv import fields, osv

class product_template(osv.osv):
    _inherit = "product.template"
    _columns = {
        'impuestos_importacion': fields.many2many('account.tax', 'product_impuestos_importacion_rel', 'prod_id', 'tax_id', 'Impuestos importacion', domain=[('parent_id', '=', False),('type_tax_use','in',['purchase','all'])]),
    }
product_template()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
