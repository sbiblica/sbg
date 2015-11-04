# -*- encoding: utf-8 -*-

#
# Este es el modulo de Topke
#
# Status 1.0 - tested on Open ERP 6.1.1
#

{
    'name' : 'bolson',
    'version' : '1.0',
    'category': 'Custom',
    'description': """Manejo de cajas chicas y liquidaciones""",
    'author': 'Rodrigo Fernandez',
    'website': 'http://solucionesprisma.com/',
    'depends' : [ 'l10n_gt_extra' ],
    'demo' : [ ],
    'data' : [ 'bolson_view.xml', 'invoice_view.xml', 'voucher_view.xml', 'bank_statement_view.xml' ],
    'installable': True,
    'certificate': '',
}
