# -*- coding: utf-8 -*-
{
    'name': "purchase_order_internal_reference",

    'summary': """
        Add product internal reference to Purchase Order and its Delivery Order report""",

    'description': """
        Add product internal reference to Purchase Order and its Delivery Order report
    """,

    'author': "Appex",
    'website': "http://appex.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Purchase',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/purchase_order_form_inherit.xml',
        'views/report_stockpicking_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
