# -*- coding: utf-8 -*-
{
    'name': 'Product Qty Secondary UoM',
    'category': 'stock',
    'version': '1.0',
    'author': 'ERP Labz',
    'website': 'erplabz.com',
    'license': 'OPL-1',
    'summary': 'Qty on hand in secondary UoM, Product Secondary UOM Qty, multiple uom, Product Secondary UOM quantity, multi uom, multiple uom, multiple unit of measure. ',
    'description': """
Qty on hand in secondary UoM, Product Secondary UOM Qty
----------------------------------------------------

""",
    'depends': ['stock'],
    'data': [
            'views/product_view_inherit.xml',

    ],
    'installable': True,
    'auto_install': True,
    "images":['static/description/banner.jpg'],
    
    'currency': 'EUR',
    'price': 12.00,

}


