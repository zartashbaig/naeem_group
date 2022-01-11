# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import timedelta, datetime


class CustomDeliveryChal(models.Model):
    _inherit = "stock.picking"

    currency_inherit_id = fields.Many2one('res.currency', string='Currency')
    manager_inherit_id = fields.Many2one('res.users', string='Sales Manager')
    account_num_inherit = fields.Char(string='Account Number')
    remarks_inherit = fields.Char(string='Remarks')
    delivery_by_inherit = fields.Char(string='Delivery by')
    delivery_to_inherit = fields.Char(string='Delivery to')
    delivery_expt_inherit = fields.Char(string='Exp. Delivery request')
    bilty_inherit = fields.Char(string='Bilty RefNo.')
    doc_no_inherit = fields.Char(string='Doc No.')
    ref_no_inherit = fields.Char(string='Doc Ref. No.')
    cancel_inherit = fields.Boolean('Cancel')
    auto_type = fields.Selection([
        ('manual', 'Manual'),
        ('auto', 'Auto')
    ], string="is Auto", default='manual')
    dc_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="DC Type")




class CustomStockMov(models.Model):
    _inherit = "stock.move"

    brand_inherit_id = fields.Many2one('product.brand', string='Brand')
    warehouse_inherit_id = fields.Many2one('stock.warehouse', string='Warehouse')
    invoice_inherit = fields.Float(string='Invoice qty')
    balance_inherit = fields.Float(string='Bal qty')
    quantity_inherit = fields.Float(string='Qty')
    bonus_qty_inherit = fields.Float(string='Bonus Qty')
    total_qty_inherit = fields.Float(string='Total Qty')
