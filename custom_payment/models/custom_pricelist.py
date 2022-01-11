# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime


class CustomPayment(models.Model):
    _inherit = "product.pricelist"

    price_code = fields.Char(string='Price Code')
    brand_id = fields.Many2one('product.brand', string='Brand')
    custom_remark = fields.Text(string='Remarks')
    currency_id = fields.Many2one('res.currency',string="Currency")

    # reference_num = fields.Char(string='Ref. Number')
    # narration_text = fields.Text(string='Narration')
    # post_date = fields.Date(string="Posting Date", default=datetime.now())
    # pv_selection = fields.Selection([
    #     ('general', 'General'),
    #     ('advance', 'Advance'),
    #     ('invoice', 'Purchase Invoice'),
    #     ('requisition', 'Purchase Requisition'),
    #     ('schedule', 'Costing Schedule'),
    #     ], string='PV Type', default='general')
    #
    # bal_amount = fields.Float(string='Balance Amount')
    #

    #
#     manufacturer_id = fields.Many2one('product_manufacturer', string='Manufacturer Code')
#     system_num = fields.Char(string='System Number')
#     port_num = fields.Char(string='Port No.')

#     origin_num = fields.Char(string='Origin')
# #