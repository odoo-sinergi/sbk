# -*- coding: utf-8 -*-
{
    'name': "SBK Cart",

    'summary': """
    Fixes SBk Cart Related Bugs
       """,

    'description': """
    """,

    'author': "K&K",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.7',

    # any module necessary for this one to work correctly
    'depends': ['base','sale', 'website_sale','theme_clarico','website_sale_options'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/cart_view.xml'
    ],
    # only loaded in demonstration mode

}