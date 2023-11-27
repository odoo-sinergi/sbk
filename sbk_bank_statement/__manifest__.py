# -*- coding: utf-8 -*-
{
    'name': "SBK BANK STATEMENT",

    'summary': """
    Enable SBK to import bank statement for keeping records
       """,

    'description': """
    """,

    'author': "TSW",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account','report_xlsx'],

    # always loaded
    'data': [
        "security/ir.model.access.csv",
        'views/sbk_bank_statement_views.xml',
        'wizard/sbk_bank_statement_wiz_views.xml'
    ],
}