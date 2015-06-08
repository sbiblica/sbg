# -*- encoding: utf-8 -*-

from openerp.osv import osv, fields
import logging

class bolson_bolson(osv.osv):
    _name = 'bolson.bolson'
    _description = 'Bolson de facturas y cheques'
    _rec_name = 'descripcion'

    def conciliar(self, cr, uid, ids, context={}):

        for obj in self.browse(cr, uid, ids, context):
            lineas = []

            total = 0
            for f in obj.facturas:
                for l in f.move_id.line_id:
                    if l.account_id.type == 'payable':
                        if not l.reconcile_id and not l.reconcile_partial_id:
                            total += l.credit - l.debit
                            lineas.append(l)
                        else:
                            raise osv.except_osv('Error!', 'La factura %s ya esta conciliada' % (f.number))

            for c in obj.cheques:
                for l in c.move_id.line_id:
                    if l.account_id.type == 'payable':
                        if not l.reconcile_id and not l.reconcile_partial_id:
                            total -= l.debit - l.credit
                            lineas.append(l)
                        else:
                            raise osv.except_osv('Error!', 'El cheque %s ya esta conciliada' % (c.number))

            for e in obj.extractos:
                for l in e.move_line_ids:
                    if l.account_id.type == 'payable':
                        if not l.reconcile_id and not l.reconcile_partial_id:
                            total += l.credit - l.debit
                            lineas.append(l)
                        else:
                            raise osv.except_osv('Error!', 'El extracto %s ya esta conciliada' % (e.name))

            for e in obj.asientos:
                for l in e.move_line_ids:
                    if l.account_id.type == 'payable':
                        if not l.reconcile_id and not l.reconcile_partial_id:
                            total += l.credit - l.debit
                            lineas.append(l)
                        else:
                            raise osv.except_osv('Error!', 'El asiento %s ya esta conciliada' % (e.name))

            if round(total) != 0:
                raise osv.except_osv('Error!', 'El total de las facturas no es igual al total de los cheques y los extractos')

            ctx = context.copy()
            ctx.update(company_id=obj.company_id.id, account_period_prefer_normal=True)
            period_ids = self.pool.get('account.period').find(cr, uid, obj.fecha, context=ctx)
            period_id = period_ids and period_ids[0] or False
            m_id = self.pool.get('account.move').create(cr, uid, {
                'ref': obj.descripcion,
                'date': obj.fecha,
                'period_id': period_id,
                'journal_id': obj.diario.id,
            });

            pares = []
            for linea in lineas:
                nueva_linea_id = self.pool.get('account.move.line').create(cr, uid, {
                    'move_id': m_id,
                    'name': linea.name,
                    'debit': linea.credit,
                    'credit': linea.debit,
                    'account_id': linea.account_id.id,
                    'partner_id': linea.partner_id.id,
                })
                pares.append([linea.id, nueva_linea_id])

            for p in pares:
                self.pool.get('account.move.line').reconcile(cr, uid, [p[0], p[1]])

            self.pool.get('account.move').button_validate(cr, uid, [m_id])
            self.write(cr, uid, obj.id, {'asiento': m_id})

        return True

    def cancelar(self, cr, uid, ids, context={}):

        for obj in self.browse(cr, uid, ids, context):
            for l in obj.asiento.line_id:
                if l.reconcile_id:
                    self.pool.get('account.move.reconcile').unlink(cr, uid, [l.reconcile_id.id])
                if l.reconcile_partial_id:
                    self.pool.get('account.move.reconcile').unlink(cr, uid, [l.reconcile_partial_id.id])
            self.pool.get('account.move').button_cancel(cr, uid, [obj.asiento.id])
            self.pool.get('account.move').unlink(cr, uid, [obj.asiento.id])

        return True

    _columns = {
        'fecha': fields.date('Fecha', required=True),
        'descripcion': fields.char('Descripción', size=40, required=True),
        'facturas': fields.one2many('account.invoice', 'bolson_id', 'Facturas'),
        'cheques': fields.one2many('account.voucher', 'bolson_id', 'Cheques'),
        'extractos': fields.one2many('account.bank.statement', 'bolson_id', 'Extractos'),
        'asientos': fields.one2many('account.move', 'bolson_id', 'Asientos'),
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'diario': fields.many2one('account.journal', 'Diario', required=True),
        'asiento': fields.many2one('account.move', 'Asiento'),
    }
    _defaults = {
        'company_id': lambda self,cr,uid,c: self.pool.get('res.company')._company_default_get(cr, uid, 'account.invoice', context=c),
    }
    _order = 'fecha desc'
bolson_bolson()
