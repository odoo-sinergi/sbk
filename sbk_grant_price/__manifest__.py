# -*- coding: utf-8 -*-
{
    'name': "SBK GRANT PRICE IN PO",

    'summary': """
    Adding Group 'Can See Price', this only group can see price in Purchase Order
       """,

    'description': """
    """,

    'author': "Appex",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase','product','stock_account'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/purchase_view.xml',
        'views/product_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}