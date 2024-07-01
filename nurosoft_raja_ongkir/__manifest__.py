# -*- coding: utf-8 -*-

{
    "name": "Biaya Pengiriman Indonesia RajaOngkir",
    "author": "Nurosoft Consulting",
    "website": "https://nurosoft.id",
    "version": "16.0.1.11",
    "category": "",
    "depends": [
        'base','web','website','sale','delivery', 'website_sale_delivery',
    ],
    "data": [
        'security/ir.model.access.csv',
        'view/setting.xml',
        'view/template.xml',
        'data/data.xml',
    ],
    "qweb": [
    ],

    'assets': {
        'web.assets_frontend': [
            'nurosoft_raja_ongkir/static/src/js/delivery.js',
            'nurosoft_raja_ongkir/static/src/css/custom.css',
        ],
    },

    'images': ['images/cover.png'],
    "price": 200.00,
    "currency": "USD",
    "license": 'OPL-1',
    'installable': True
}
