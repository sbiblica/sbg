# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw
from .. import util
import locale

class report_nota_credito(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(report_nota_credito, self).__init__(cr, uid, name, context=context)
        locale.setlocale(locale.LC_ALL, 'en_US.utf8')
        self.localcontext.update({
            'time': time,
            'util': util,
            'lineas_factura': self.lineas_factura,
            'locale': locale,
        })

    def lineas_factura(self, lineas):

        new_lines = []

        for l in lineas:
            if l.price_unit != 0:
                new_lines.append(l)

        return new_lines

report_sxw.report_sxw(
    'report.nota.credito.sin.unidad',
    'account.invoice',
    'sbg/reportes/nota_credito_sin_unidad.rml',
    parser=report_nota_credito
)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
