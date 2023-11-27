# -*- coding: utf-8 -*-
{
    'name': "SBK Sample Product",

    'summary': """
    Quotation option for sample product
       """,

    'description': """
    Another column added “is sample?” with a value of true/false. So when they check that, the sell price in the quotaton will become 0, and it will be marked in the system as a sample product that have been sent to customer.
Then they want to create a sample report for each customer, see how many sample the customer have received
so when create a sample report, just need to find those that have the price is 0, also, for sample report, they want to have the ability to select the time frame for it.
    """,

    'author': "K&K",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/sale_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}