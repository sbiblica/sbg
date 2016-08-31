# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import openerp.addons.decimal_precision as dp

class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _order = "date_invoice desc"

    def limite_credito(self, cr, uid, ids):
        for invoice in self.browse(cr, uid, ids):
            if invoice.journal_id.punto_de_venta == True:
                return True
            limite_credito = invoice.partner_id.credit_limit
            credito_actual = invoice.partner_id.credit
        if (limite_credito - credito_actual - invoice.amount_total) < 0:
            raise osv.except_osv('Cliente rebasó crédito autorizado', 'Favor pedir autorización para poder facturar')
            return False
        else:
            return True

    def _tienda(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for obj in self.browse(cr, uid, ids, context):

            origen_ids = self.pool.get('pos.order').search(cr, uid, [('name', '=', obj.origin)])

            if origen_ids:
                origen = self.pool.get('pos.order').browse(cr, uid, origen_ids)[0]
                result[obj.id] = origen.shop_id.name
                return result
            else:
                origen_ids = self.pool.get('sale.order').search(cr, uid, [('name', '=', obj.origin)])
                if origen_ids:
                    origen = self.pool.get('sale.order').browse(cr, uid, origen_ids)[0]
                    result[obj.id] = origen.shop_id.name
                    return result

        result[obj.id] = ""

        return result


    def _numero_factura(self, cr, uid, ids, field_name, arg, context):
        result = {}

        for factura in self.browse(cr, uid, ids):
            if factura.state != "cancel":
                result[factura.id] = factura.number
            else:
                result[factura.id] = factura.internal_number

        return result

    def expand_packs(self, cr, uid, ids, context={}, depth=1):
        if depth == 10:
            return
        updated_invoices = []
        if type(ids) in [type(int()), type(long())]:
            ids = [ids]
        for invoice in self.browse(cr, uid, ids, context):

            # The reorder variable is used to ensure lines of the same pack go right after their
            # parent.
            # What the algorithm does is check if the previous item had children. As children items
            # must go right after the parent if the line we're evaluating doesn't have a parent it
            # means it's a new item (and probably has the default 10 sequence number - unless the
            # appropiate c2c_pos_sequence module is installed). In this case we mark the item for
            # reordering and evaluate the next one. Note that as the item is not evaluated and it might
            # have to be expanded it's put on the queue for another iteration (it's simple and works well).
            # Once the next item has been evaluated the sequence of the item marked for reordering is updated
            # with the next value.
            sequence = -1
            reorder = []
            last_had_children = False
            for line in invoice.invoice_line:
                if last_had_children and not line.pack_parent_line_id:
                    reorder.append( line.id )
                    if line.product_id.pack_line_ids and not invoice.id in updated_invoices:
                        updated_invoices.append( invoice.id )
                    continue

                sequence += 1

                if sequence > line.sequence:
                    self.pool.get('account.invoice.line').write(cr, uid, [line.id], {
                        'sequence': sequence,
                    }, context)
                else:
                    sequence = line.sequence

                if not line.product_id:
                    continue

                tax_array = []

                for tax in line.invoice_line_tax_id:
                    tax_array.append((4, tax.id))

                # If pack was already expanded (in another create/write operation or in
                # a previous iteration) don't do it again.
                if line.pack_child_line_ids:
                    last_had_children = True
                    continue
                last_had_children = False

                if line.product_id.pack_line_ids:
                    self.pool.get('account.invoice.line').write(cr, uid, [line.id], {
                        'discount': 100,
                    }, context)

                for subline in line.product_id.pack_line_ids:
                    sequence += 1

                    subproduct = subline.product_id
                    quantity = subline.quantity * line.quantity
                    discount = 100.0

                    # Obtain product name in partner's language
                    ctx = {}
                    subproduct_name = self.pool.get('product.product').browse(cr, uid, subproduct.id, ctx).name

                    cta = None
                    if invoice.type in ('out_invoice','out_refund'):
                        cta = subproduct.product_tmpl_id.property_account_income.id
                        if not cta:
                            cta = subproduct.categ_id.property_account_income_categ.id
                    else:
                        cta = subproduct.product_tmpl_id.property_account_expense.id
                        if not cta:
                            cta = subproduct.categ_id.property_account_expense_categ.id

                    vals = {
                        'sequence': sequence,
                        'origin': line.origin,
                        'name': '%s%s' % ('> '* (line.pack_depth+1), subproduct_name),
                        'invoice_id': invoice.id,
                        'uos_id': subproduct.uom_id.id,
                        'product_id': subproduct.id,
                        'account_id': cta,
                        'price_unit': line.price_unit * quantity,
                        'discoun': 0,
                        'quantity': quantity,
                        'invoice_line_tax_id': tax_array,
                        'note': line.note,
                        'account_analytic_id': line.account_analytic_id.id,
                        'pack_parent_line_id': line.id,
                        'pack_depth': line.pack_depth + 1,
                    }

                    self.pool.get('account.invoice.line').create(cr, uid, vals, context)
                    if not invoice.id in updated_invoices:
                        updated_invoices.append( invoice.id )

                for id in reorder:
                    sequence += 1
                    self.pool.get('account.invoice.line').write(cr, uid, [id], {
                        'sequence': sequence,
                    }, context)

        if updated_invoices:
            # Try to expand again all those orders that had a pack in this iteration.
            # This way we support packs inside other packs.
            self.expand_packs(cr, uid, ids, context, depth+1)
        return True

    _columns = {
        'write_date': fields.datetime("Write date"),
        'tienda': fields.function(_tienda, type='char', method=True, string='Tienda'),
        'add_disc':fields.float('Additional Discount(%)',digits=(4,2),readonly=True, states={'draft':[('readonly',False)]}),
        'numero_factura': fields.function(_numero_factura, type='char', method=True, string='Numero Factura'),
        'facturas_asociadas': fields.many2many('account.invoice', 'account_invoice_asociadas_rel', 'factura_id', 'factura_asociada_id', 'Facturas asociadas'),
        'cliente_donacion_id': fields.many2one('res.partner', 'Cliente de donacion'),
    }
    _defaults={
        'add_disc': 0.0,
    }
account_invoice()


class account_invoice_line(osv.osv):
    _inherit = 'account.invoice.line'

    _columns = {
        'sequence': fields.integer('Sequence', help="Gives the sequence order when displaying a list of sales order lines."),
        'pack_depth': fields.integer('Depth', required=True, help='Depth of the product if it is part of a pack.'),
        'pack_parent_line_id': fields.many2one('account.invoice.line', 'Pack', help='The pack that contains this product.'),
        'pack_child_line_ids': fields.one2many('account.invoice.line', 'pack_parent_line_id', 'Lines in pack', help=''),
    }

    _defaults = {
        'pack_depth': lambda *a: 0,
        'sequence': lambda *a: 10,
    }
    _order = 'sequence, id asc'
account_invoice_line()
