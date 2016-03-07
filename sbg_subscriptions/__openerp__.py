# -*- coding: utf-8 -*-
{
    'name': "Subscriptions Management for SBG",

    'summary': """
        Subscriptions management module for Bible Society of Guatemala
    """,

    'description': """
        Subscriptions management module for Bible Society of Guatemala

        Manages subscriptions to clubs and courses
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
        'views/partner_view.xml',
        'views/sbg_subscription_services.xml',
        # 'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}