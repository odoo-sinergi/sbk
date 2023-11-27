# -*- coding: utf-8 -*-
{
    'name': "SBK PURCHASE",
    'summary': """Modifications of Purchase Modules based on SBK request
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
    'depends': ['base','purchase'],

    # always loaded
    'data': [
        'views/purchase_order_views.xml',
        'report/purchase_order.xml'
        # 'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}