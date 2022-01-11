# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'custom_delivery_challan',
    'version': '0.1',
    'sequence': 10,
    'description': """ 
    this module keeps the personal data
    """,
    'category': 'Accounting/Accounting',
    'website': 'https://cybat.com',
    'depends': ['stock',
                'product_brand_inventory',
                'account',
                ],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_chal.xml',
        'views/custom_delivery.xml',
        'views/product_template_inherit.xml',
    ],
    'demo': ['demo/demo.xml', ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
