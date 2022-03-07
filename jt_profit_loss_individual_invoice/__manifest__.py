# -*- coding: utf-8 -*-
##########################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
##########################################################################

{
    'name': 'Invoice wise COGS and Profit/Loss',
    'version': '14.0.1.0.0',
    'author': 'Jupical Technologies Pvt. Ltd.',
    'maintainer': 'Jupical Technologies Pvt. Ltd.',
    'depends': ['sale_management', 'stock', 'stock_account'],
    'summary': "Invoice wise COGS and Profit/Loss",
    'category': 'account',
    "description": """
    """,
    'data': [
        'views/account_view.xml',
        'report/account_invoice_report.xml'
    ],
    'website': 'http://www.jupical.com',
    'live_test_url': 'https://www.youtube.com/channel/UC2x2iEL-oW3LrwmB3OO_3hQ/videos',
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': ['static/description/poster_image.png'],
    'price': 15.00,
    'currency': 'USD'
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
