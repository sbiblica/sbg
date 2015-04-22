# -*- encoding: utf-8 -*-

#
# Este es el modulo de conciliación bancaria
#
# Status 1.0 - tested on Open ERP 7.0
#

{
    'name' : 'conciliacion_bancaria',
    'version' : '1.0',
    'category': 'Custom',
    'description': """Manejo de conciliación bancaria""",
    'author': 'Rodrigo Fernandez',
    'website': 'http://solucionesprisma.com/',
    'depends' : [ 'account', 'l10n_gt' ],
    'init_xml' : [ ],
    'demo_xml' : [ ],
    'update_xml' : [
        'account_move_line.xml',
        'conciliar.xml',
        'reportes.xml'
    ],
    'installable': True,
    'certificate': '',
}
