# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime


class CustomPayment(models.Model):
    _inherit = "account.payment"

    pv_num = fields.Char(string='PV No.')
    reference_num = fields.Char(string='Ref. Number')
    narration_text = fields.Text(string='Narration')
    post_date = fields.Date(string="Posting Date", default=datetime.now())
    pv_selection = fields.Selection([
        ('general', 'General'),
        ('advance', 'Advance'),
        ('invoice', 'Purchase Invoice'),
        ('requisition', 'Purchase Requisition'),
        ('schedule', 'Costing Schedule'),
        ], string='PV Type', default='general')

    bal_amount = fields.Float(string='Balance Amount')


