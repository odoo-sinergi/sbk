# -*- coding: utf-8 -*-
{
    'name': "SBK SALE, SAMPLE, CRM PRODUCT SUMMARY REPORT",

    'summary': """
        - Sale Order Line Summary report
        - Sample Sale Order Line Summary report
        - Product in CRM Lead Summary report
        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Appex",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.3',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','stock','account','purchase','multi_currency_expansion', 'sbk_crm_product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/asset.xml',
        'views/partner_button.xml',
        'views/crm_product_view.xml',
        'report/sale_order_line_report_template.xml',
        'report/delivery_order_template.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}