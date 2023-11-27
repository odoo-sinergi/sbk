# -*- coding: utf-8 -*-
{
    'name': "SBK INVOICE REPORT",

    'summary': """
        - SBK Proforma Invoice Report
        - SBK Invoice Report
        - Roman format in prefix Sequence
       """,

    'description': """
    """,

    'author': "Appex",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.5',

    # any module necessary for this one to work correctly
    'depends': ['base','account','stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/asset.xml',
        'views/invoice_view.xml',
        'report/sbk_invoice_report.xml',
        'report/pro_forma_sale_order.xml',
        'data/data.xml',
        'views/sale_order.xml',
        'views/ir_sequence.xml',
        'views/email_template_so.xml',
        'wizard/sales_report_views.xml'

    ],
    # only loaded in demonstration mode
    'demo': [

    ],
    'css': ['static/src/css/sbk_invoice_report.css'],
}