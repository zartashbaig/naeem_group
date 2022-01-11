# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime


class CustomPayment(models.Model):
    _inherit = "account.payment"

    pv_num = fields.Char(string='PV No.')
    reference_num = fields.Char(string='Reference No.')
    narration_text = fields.Text(string='Narration')
    post_date = fields.Date(string="Posting Date", default=datetime.now())
    pv_selection = fields.Selection([
        ('general', 'General'),
        ('advance', 'Advance'),
        ('invoice', 'Purchase Invoice'),
        ('requisition', 'Purchase Requisition'),
        ('schedule', 'Costing Schedule'),
        ], string='PV Type', default='general')
    rv_selection = fields.Selection([
        ('general', 'General'),
        ('advance', 'Advance'),
        ('invoice', 'Sales Invoice'),
        ('jv', 'Journal Voucher'),
    ], string='RV Type', default='general')
    rv_category = fields.Selection([
        ('pdc', 'PDC'),
    ], string='RV Category')
    bal_amount = fields.Float(string='Balance Amount')


