# -*- coding: utf-8 -*-
{
    'name': "custom_purchase_sys",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    "depends": ["purchase_stock", 'account', 'product_brand_inventory', 'utm', 'crm'],

    # always loaded
    'data': [
        'security/group.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'wizard/create_invoice.xml',
        'wizard/quotation_wizard_view.xml',
        'views/views.xml',
        'views/quotation.xml',
        'views/purchase.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
