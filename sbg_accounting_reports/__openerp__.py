# -*- coding: utf-8 -*-
{
    'name': "Accounting reports for SBG",

    'summary': """
        Accounting reports module for Bible Society of Guatemala
    """,

    'description': """
        Special accounting reports module for Bible Society of Guatemala

        Includes official reports for SAT
    """,

    'author': "Dynamic Development Studios",
    'website': "http://www.DynamicDevStudios.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'sbg_accounting_reports_menu.xml',
        'wizard/sbg_fiscal_general_ledger_wizard.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}