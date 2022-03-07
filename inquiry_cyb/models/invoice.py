# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class ProductCategoryBrandExt(models.Model):
    _inherit = "product.category"

    brand_id = fields.Many2one('product.brand', string="Brand")

    @api.depends('name', 'brand_id.name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for category in self:
            if category.parent_id and category.brand_id:
                category.complete_name = '%s / %s / %s' % (category.brand_id.name,category.parent_id.complete_name,  category.name)
            elif category.parent_id:
                category.complete_name = '%s / %s' % (category.parent_id.complete_name, category.name)
            else:
                category.complete_name = category.name

    # @api.constrains('parent_id', 'brand_id')
    # def _check_category_recursion(self):
    #     if not self._check_recursion():
    #         raise ValidationError(_('You cannot create recursive Categories & Brands.'))
    #     return True


class SaleOrderExt(models.Model):
    _inherit = "account.move"

    # quotation_sale_many_ids = fields.Many2many('cyb.quotation', 'cyb_quotation_rel', string='Quotation Lines')
    count = fields.Integer(compute="_compute_discount_total", string='SN (Total)', store=True, readonly=1)
    total_qty = fields.Float(string='Total QTY', store=True, readonly=True, compute='_amount_all_qty', tracking=4)
    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        string="Discount %",
        currency_field="currency_id",
        store=True,
    )
    net_amount = fields.Float(string='Net Amount', readonly=True, store=True)

    @api.depends('invoice_line_ids.quantity')
    def _amount_all_qty(self):
        """
        Compute the total Quantity of the Customer Invoice.
        """
        for invoice in self:
            total_qty = 0
            for line in invoice.invoice_line_ids:
                if line.product_id:
                    total_qty += line.quantity
            invoice.update({
                'total_qty': total_qty,
            })

    @api.depends("invoice_line_ids.prod_total_discount")
    def _compute_discount_total(self):
        for invoice in self:
            count = 0
            for lines in invoice.invoice_line_ids:
                if lines.product_id:
                    count += 1
            discount_total = sum(invoice.invoice_line_ids.mapped('prod_total_discount'))

            invoice.update(
                {
                    "count": count,
                    "discount_total": discount_total,
                }
            )


class SaleOrderLineExt(models.Model):
    _inherit = "account.move.line"

    # remarks = fields.Text(string="Remarks")
    bonus_quantity = fields.Float(string='Bonus Qty', default=1.0)
    prod_total_discount = fields.Float('Disc. Amount', readonly=True, store=True)

    # @api.depends('quantity', 'discount', 'price_unit', 'tax_ids')
    # def _compute_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         if line.quantity > 0:
    #             price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #             taxes = line.tax_ids.compute_all(price, line.invoice_line_ids.currency_id, line.quantity,
    #                                             product=line.product_id)
    #             total_prod_price = line.quantity * line.price_unit
    #             prod_total_discount = total_prod_price*(line.discount / 100)
    #             line.update({
    #                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #                 'price_total': taxes['total_included'],
    #                 'price_subtotal': taxes['total_excluded'],
    #                 'prod_total_discount': prod_total_discount,
    #             })
    #         if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
    #                 'account.group_account_manager'):
    #             line.tax_ids.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_ids.id])

    @api.model
    def _get_price_total_and_subtotal_model(self, price_unit, quantity, discount, currency, product, partner, taxes, move_type):
        ''' This method is used to compute 'price_total' & 'price_subtotal'.

        :param price_unit:  The current price unit.
        :param quantity:    The current quantity.
        :param discount:    The current discount.
        :param currency:    The line's currency.
        :param product:     The line's product.
        :param partner:     The line's partner.
        :param taxes:       The applied taxes.
        :param move_type:   The type of the move.
        :return:            A dictionary containing 'price_subtotal' & 'price_total'.
        '''
        res = {}

        # Compute 'price_subtotal'.
        line_discount_price_unit = price_unit * (1 - (discount / 100.0))
        subtotal = quantity * line_discount_price_unit

        total_prod_price = quantity * price_unit
        prod_total_discount = total_prod_price * (discount / 100)
        # Compute 'price_total'.
        if taxes:
            force_sign = -1 if move_type in ('out_invoice', 'in_refund', 'out_receipt') else 1
            taxes_res = taxes._origin.with_context(force_sign=force_sign).compute_all(line_discount_price_unit,
                quantity=quantity, currency=currency, product=product, partner=partner, is_refund=move_type in ('out_refund', 'in_refund'))
            res['price_subtotal'] = taxes_res['total_excluded']
            res['price_total'] = taxes_res['total_included']
            res['prod_total_discount'] = prod_total_discount
        else:
            res['price_total'] = res['price_subtotal'] = subtotal
        #In case of multi currency, round before it's use for computing debit credit
        if currency:
            res = {k: currency.round(v) for k, v in res.items()}
        return res




