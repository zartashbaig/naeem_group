# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime


class CustomDelivery(models.Model):
    _name = 'product_manufacturer'

    custom_manu_name = fields.Char(string='Manufacturer Name')
    custom_manu_code = fields.Char(string='Manufacturer Code')

