# -*- coding: utf-8 -*-
{
    'name': "sales_budget_plan",

    'summary': """
        Create budget plan in sales""",

    'description': """
        Create budget plan in sales. This include: product, time period, budget amount, and who(which manager account) create this
    """,

    'author': "Appex",
    'website': "appex.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/budget_plan_menu.xml',
        'views/budget_plan_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'application': True,
}
