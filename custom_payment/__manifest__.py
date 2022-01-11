# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'custom_payment',
    'version': '0.1',
    'sequence': 11,
    'description': """ 
    this module keeps the personal data
    """,
    'category': 'Accounting/Accounting',
    'website': 'https://cybat.com',
    'depends': ['stock',
                'product_brand_inventory',
                'account',
                'sale_management',
                ],
    'data': [
        # 'security/ir.model.access.csv',
        'views/payments.xml',
        'views/custom_pricelist.xml',
    ],
    'demo': ['demo/demo.xml', ],

    'installable': True,
    'application': True,
    'auto_install': False,
}
