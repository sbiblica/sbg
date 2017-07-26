# -*- coding: utf-8 -*-
{
    'name': "Volunteer Management for SBG",

    'summary': """
        Volunteers management module for Bible Society of Guatemala
    """,

    'description': """
        Volunteers management module for Bible Society of Guatemala

        Manages volunteers and their information
    """,

    'author': "Dynamic Development Studios",
    'website': "http://www.DynamicDevStudios.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/main_menu.xml',
        'views/sbg_churches.xml',
        'views/sbg_education_levels.xml',
        'views/sbg_languages.xml',
        'views/sbg_civil_status.xml',
        'views/sbg_professions_talents.xml',
        'views/sbg_projects.xml',
        'views/sbg_volunteer_groups.xml',
        'views/res_partner.xml',
        'views/sbg_volunteer_events.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}