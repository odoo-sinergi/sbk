# -*- coding: utf-8 -*-
{
    'name': "fleet_capacity",

    'summary': """
        Fleet Capacity""",

    'description': """
        Fleet Capacity
    """,

    'author': "Appex",
    'website': "http://appex.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Human Resources',
    'version': '11.0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'fleet'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/carton_views.xml',
        'views/fleet_vehicle_views_inherit.xml',
        'views/fleet_capacity_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
