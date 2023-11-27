# -*- coding: utf-8 -*-
{
    'name': "change_paper_format_viipc",

    'summary': """
        Change format of Quotation/Invoice/Order documents""",

    'description': """
        Change format of Quotation/Invoice/Order documents
    """,

    'author': "Appex",
    'website': "http://www.appex.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'web', 'account', 'website'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'reports/sale_report_templates_edit.xml',
        'reports/external_layout_clean_edit.xml',
        'reports/report_invoice_document_edit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
