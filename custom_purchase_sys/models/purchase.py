# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class PurchaseDiscount(models.Model):
    _inherit = "purchase.order"

    quotation_sale_many_ids = fields.Many2many('cyb.quotation.purchase', string='Quotation Lines')
    net_amount = fields.Float(string='Net Amount', readonly=True, store=True)
    count = fields.Integer(compute="_compute_discount_total", string='SN (Total)', store=True, readonly=1)
    total_qty = fields.Float(string='Total QTY', store=True, readonly=True, compute='_amount_all_qty', tracking=4)
    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        string="Discount %",
        currency_field="currency_id",
        store=True,
    )

    @api.depends('order_line.product_qty')
    def _amount_all_qty(self):
        """
        Compute the total Quantity of the SO.
        """
        for order in self:
            total_qty = 0
            for line in order.order_line:
                total_qty += line.product_qty
            order.update({
                'total_qty': total_qty,
            })

    @api.depends("order_line.prod_total_discount")
    def _compute_discount_total(self):
        for order in self:
            count = 0
            for lines in order.order_line:
                if lines.product_id:
                    count += 1
            discount_total = sum(order.order_line.mapped('prod_total_discount'))

            order.update(
                {
                    "count": count,
                    "discount_total": discount_total,
                }
            )


class PurchaseLineDiscount(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float('Discount%')
    bonus_quantity = fields.Float(string='Bonus Qty', default=1.0)
    prod_total_discount = fields.Float('Disc. Amount', readonly=True, store=True)
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    remarks = fields.Text(string="Remarks")



    @api.depends('product_qty', 'price_unit', 'taxes_id','discount')
    def _compute_amount(self):
        for line in self:
            if line.product_qty > 0:
                taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty, product=line.product_id, partner=line.order_id.partner_id)
                if line.discount:
                    discount = (line.price_unit * line.discount * line.product_qty)/100
                    total_prod_price = line.product_uom_qty * line.price_unit
                    prod_total_discount = total_prod_price*(line.discount / 100)
                    line.update({
                        'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_total': taxes['total_included'] ,
                        'price_subtotal': taxes['total_excluded'] - discount,
                        'prod_total_discount': prod_total_discount,
                    })
                else:
                    line.update({
                        'price_tax': taxes['total_included'] - taxes['total_excluded'],
                        'price_total': taxes['total_included'],
                        'price_subtotal': taxes['total_excluded'],
                    })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
