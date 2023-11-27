# -*- coding: utf-8 -*-
{
    'name': "SBK ECommerce Invoice",

    'summary': """
    E-commerce sale will have their own shipping method
       """,

    'description': """
    We will have shipping methods.
If the shipping method is drop ship, they want to remove the SBK logo and SBK address from the invoice.
On Odoo, SBK will need to create a sale order. In the sale order, we need to indicate is this a e-commerce sale. And e-commerce sale will have their own shipping method.
So in the sale order, we need to add in two fields:
1- a check box that says "is e-commerce sale?”
2- if they tick on the checkbox, then we will have two more fields, else these two fields will be greyed out or not appear:
    - e-commerce invoice number (manually input)
    - shipping method. (a drop down selection box with one option: drop-ship)
If we have chosen e-commerce AND drop ship, the invoice when print out will not have logo and SBK address. If we didnt choose shipping method as drop ship, OR we didnt choose this Sale Order as a e-commerce sale, then dont need to remove the logo and SBK address.
Remember that, the e-commerce invoice number once inputted, will be appear when print out invoice for this sale order too.
    """,

    'author': "K&K",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.7',

    # any module necessary for this one to work correctly
    'depends': ['base','sale', 'account'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/invoice_view.xml',
        'views/sale_view.xml',
        'views/shipping_method_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}