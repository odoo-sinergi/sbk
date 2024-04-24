# -*- coding: utf-8 -*-
{
    'name': "SDT Custom Form SBK",

    'summary': """
        Custom Form""",

    'description': """
        Custom Form
    """,

    'author': "Sinergi Data Totalindo, PT",
    'website': "http://www.sinergidata.co.id",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '16.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'account',
        'stock',
    ],

    # always loaded
    'data': [
        'report/report_templates.xml',
        'report/purchase_order.xml',
        'report/report_invoice.xml',
        'report/report_deliveryslip.xml',
        'report/report_saleorder_pro_forma.xml',
        'views/base_document_layout_views.xml',
    ],
    # only loaded in demonstration mode
}