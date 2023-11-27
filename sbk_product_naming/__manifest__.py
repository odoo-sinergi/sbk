# -*- coding: utf-8 -*-
{
    'name': "SBK Naming Product",

    'summary': """
    Different Namings of product
       """,

    'description': """
A product name that only the admin and the vendor know about. This one we agree to use Vendor Product Name. This name only used when purchased product from vendor and creating Purchase Order. When there is product coming from Vendor to warehouse. We will use Product Name and not Vendor Product Name so the warehouse guy will know which product they are taking in. In the delivery slip from Vendor to SBK, we will not show Vendor Product name, we only show Product Name. Vendor Product Name will only be shown to the one who create the Purchase Order.
A Product Name that everyone can see, except the customer. This one we will use Odoo’s Product Name
Printout Name: a name that only for print out. This one is added in and can be edit in Quotation, Sale Order, Invoice, Delivery Slip. Customer will see print out name in Quotation, Sale Order, Invoice, Delivery slip.When we print out or send email these document, we need to hide Product Name on these document and only use Print out Name
    """,

    'author': "TSW",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','purchase','stock'],

    # always loaded
    'data': [
        'security/security.xml',
        'views/purchase_views.xml',
        'views/sale_views.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}