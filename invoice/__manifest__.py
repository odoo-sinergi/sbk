# -*- coding: utf-8 -*-
{
    'name': "Invoices",

    'summary': """
        
        """,

    'description': """
        Manage Invoice Directly from Desktop
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/fee_sequence.xml',
        'views/views.xml',
        'wizard/inv_summary_view.xml',
        'wizard/sale_man_inv_summary_view.xml',
        'views/report.xml',
        'views/inv_report.xml',
        'views/saleman_inv_template.xml'


    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}