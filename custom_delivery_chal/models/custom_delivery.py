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
    bilty_inherit = fields.Char(string='Bilty Ref No.')
    doc_no_inherit = fields.Char(string='Doc No.')
    ref_no_inherit = fields.Char(string='Ref No.')
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

class DOExt(models.Model):
    _inherit = "stock.move.line"

    bonus_quantity = fields.Float(string='Bonus Qty', compute='_gets_data')
    ordered_quantity = fields.Float(string='Ordered Qty', compute='_gets_data')
    qty_done = fields.Float('Done', default=0.0, digits='Product Unit of Measure', copy=False)
    total_qty_inherit = fields.Float(string='Total Qty', compute='_compute_amount_total')
    product_uom_qty = fields.Float('Reserved', default=0.0, digits='Product Unit of Measure', required=True)
    brand_id = fields.Many2one('product.brand', string='Brand')
    wh_id = fields.Many2one('stock.warehouse', string='Warehouse')


    @api.model
    def _gets_data(self):
        self.bonus_quantity = 0.0
        self.ordered_quantity = 0.0

        for move in self:
            # if not move.move_lines and not move.move_line_ids:
            if not (move.picking_id and move.picking_id.group_id):
                continue
            picking = move.picking_id
            sale_order = self.env['sale.order'].sudo().search([
                ('procurement_group_id', '=', picking.group_id.id)], limit=1)
            if sale_order:
                for line in sale_order.order_line:
                    if line.product_id.id != move.product_id.id:
                        continue
                    move.update({
                        'bonus_quantity': line.bonus_quantity,
                        'ordered_quantity': line.product_uom_qty,
                    })
            else:
                move.bonus_quantity = False

    @api.depends('bonus_quantity', 'total_qty_inherit', 'ordered_quantity')
    def _compute_amount_total(self):
        self.total_qty_inherit = self.bonus_quantity + self.ordered_quantity

    # @api.depends('bonus_quantity', 'product_uom_qty', 'qty_done')
    # def _compute_amount_done(self):
    #     self.qty_done = self.bonus_quantity + self.product_uom_qty
