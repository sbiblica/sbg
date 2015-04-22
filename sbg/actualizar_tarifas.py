# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields

class sbg_actualizar_tarifas(osv.osv_memory):
    _name = 'sbg.actualizar_tarifas'
    _description = 'Proceso para actualizar las tarifas de los clientes'

    def actualizar(self, cr, uid, ids, context={}):

        xx = 0
        for obj in self.browse(cr, uid, ids, context):

            pricelist_ids = self.pool.get('product.pricelist').search(cr, uid, [('name', '!=', 'XYZ')])
            tarifas = {}
            for pricelist in self.pool.get('product.pricelist').browse(cr, uid, pricelist_ids):
                tarifas[pricelist.name] = pricelist.id

            cr.execute("select res_id, clase from sbg_clasifica")

            for row in cr.fetchall():
                xx += 1
                if xx % 100 == 0:
                    pass

                if row[1] in tarifas:
                    partner_id = self.pool.get('res.partner').search(cr, uid, [('id', '=', row[0])])
                    if partner_id:
                        self.pool.get('res.partner').write(cr, uid, [row[0]], {'property_product_pricelist':tarifas[row[1]]})

        return True

sbg_actualizar_tarifas()
