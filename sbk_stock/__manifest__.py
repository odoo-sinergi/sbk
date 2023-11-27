# -*- coding: utf-8 -*-
{
    'name': "SBK STOCK CUSTOM",

    'summary': """
        - Add field supplier_lot_number to Lot and show in Delivery Slip report
        - Add field note at Move Line in Stock Picking
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
    'depends': ['base','product_expiry'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/asset.xml',
        'views/lot.xml',
        # 'report/do_report.xml',
        'report/delivery_report.xml',
        'views/stock_picking.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}