# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime


class CustomDeliveryChal(models.Model):
    _inherit = "product.template"

    # brand_id = fields.Many2one('product.brand', string='Brand')
    manufacturer_id = fields.Many2one('product_manufacturer', string='Manufacturer Code')
    system_num = fields.Char(string='System Number')
    port_num = fields.Char(string='Port No.')
    serial_num = fields.Char(string='Serial No.')
    origin_num = fields.Char(string='Origin')
