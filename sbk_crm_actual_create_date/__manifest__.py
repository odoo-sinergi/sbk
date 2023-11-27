# -*- coding: utf-8 -*-
{
    'name': "SBK Actual Create date",

    'summary': """
    create for SBK data import
       """,

    'description': """
for internal use only
    """,

    'author': "Appex",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','crm'],

    # always loaded
    'data': [
        'views/views.xml',
    ],
}