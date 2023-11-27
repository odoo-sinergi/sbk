# -*- coding: utf-8 -*-

{
    'name': 'VIIPC Export Customer Tax',
    'summary': """Export Customer Zero Tax for ViiPC""",
    'version': '12.0.1.0.0',
    'description': """Remove tax when Customer is a export customer requested by ViiPC""",
    'author': 'Appex Private Limited',
    'company': 'Appex Private Limited',
    'website': 'https://www.appex.co',
    'category': 'Extra Tools',
    'depends': ['base', 'sale'],
    'license': 'AGPL-3',
    'data': [
        'views/res_partner_view.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,

}
