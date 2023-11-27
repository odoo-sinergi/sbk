# -*- coding: utf-8 -*-
{
    'name': "customer_project_count",

    'summary': """
        adding a project-count button to customers' detail page""",

    'description': """
        adding a project-count button to customers' detail page
    """,

    'author': "Appex",
    'website': "http://appex.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Project',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'project'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/project_views.xml',
        'views/res_partner_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
