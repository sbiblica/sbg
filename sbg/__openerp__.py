# -*- encoding: utf-8 -*-

#
# Este es el modulo para toda la configuracion y funcionalidad del proyecto
# de La Sociedad Biblica de Guatemala.
#
# Status 1.0 - tested on Open ERP 5.0.6
#

{
    'name' : 'sbg',
    'version' : '1.0',
    'category': 'Custom',
    'description': """Este es el modulo para toda la configuracion y funcionalidad del proyecto de La Sociedad Biblica de Guatemala.""",
    'author': 'Rodolfo Borstcheff',
    'website': 'http://solucionesprisma.com/',
    'depends' : ['account_voucher','point_of_sale','stock'],
    'demo' : [ ],
    'data' : [
        'account_view.xml',
        'account_move_line_conciliar.xml',
        'actualizar_tarifas_view.xml',
        'catalogos_view.xml',
        'clubs_view.xml',
        'diferencias_inventario_view.xml',
        'estado_de_cuenta_view.xml',
        #'hr_view.xml',
        'invoice_view.xml',
        #'invoice_workflow.xml',
        'product_view.xml',
        'sale_view.xml',
        'sale_workflow.xml',
        'voucher_view.xml',
        'partner_view.xml',
        'point_of_sale_view.xml',
        'stock_view.xml',
        'reportes.xml',
        'security/account_security.xml'
    ],
    'installable': True,
    'certificate': '',
}
