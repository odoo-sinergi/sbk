# -*- coding: utf-8 -*-
{
    'name': "SBK PRINT LOT & PRODUCT",

    'summary': """
        - LOT & PRODUCT  REPORT PRINT
        - Format pager for lot , format page for product
      """,

    'description': """
    """,

    'author': "Appex",
    'website': "http://www.appex.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock'],

    # always loaded
    'data': [
        'report/report_action_lot.xml',
        'report/report_product.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}