# -*- coding: utf-8 -*-
{
    'name': "Statistical Reports for SBG",

    'summary': """
        Statistical reports for Bible Society of Guatemala
    """,

    'description': """
        Custom statistical reports for Bible Society of Guatemala.
    """,

    'author': "Dynamic Development Studios",
    'website': "http://www.DynamicDevStudios.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale', 'point_of_sale', 'rep_ventas', 'account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sbg_sales_view.xml',
        'views/sbg_variables.xml',
        'views/sbg_indexes.xml',
        'views/sbg_indexes_report.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}