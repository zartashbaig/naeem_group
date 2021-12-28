# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'inquiry_cyb',
    'version' : '0.1',
    'description': """ 
    this module keeps the personal data
    """,
    'category': 'Uncategorized',
    'website': 'https://cybat.com',
    'depends' : ['base','sale','sale_management','sale_crm','sales_team', 'utm', 'product_brand_inventory', 'account', 'purchase', 'stock'],

    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/create_invoice.xml',
        'wizard/quotation_wizard_view.xml',
        # 'wizard/sequence.xml',
        'views/inquiry_mail.xml',
        'views/inquiry.xml',
        'views/quotation.xml',
        'views/invoice.xml',
    ],
    'demo': [],

    'installable': True,
    'application': True,
    'auto_install': False,
}
