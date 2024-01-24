# -*- encoding: utf-8 -*-

{
    'name': 'SDT UDF SBK',
    'version': '1.0',
    'category': 'Inventory',
    'author':'Sinergi Data Totalindo, PT',
    'description': """UDF SBK
    """,
    'summary': 'UDF SBK',
    'website': 'http://sinergidata.co.id',
    'data': [
        'views/purchase_order.xml',
        'views/stock_picking.xml',
        'views/account_move.xml',
    ],
    'depends': ['base','delivery','stock','purchase','account'],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 105,
    'license': 'AGPL-3',
}
