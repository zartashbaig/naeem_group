# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class InquiryInvoice(models.TransientModel):
    _name = 'quotation.wizard'

    new_order_line_ids = fields.One2many('getsale.quotation', 'new_order_line_id', string="Order Line")
    partner_id = fields.Many2one('res.partner', string='Customer', readonly=True, store=True)
    date_order = fields.Datetime(string='Order Date', readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    quotation_Expiration = fields.Date(string="Expiration", related="so_id.quotation_Expiration")
    so_id = fields.Many2one('cyb.quotation', string="Quotation ID", )
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead", related="so_id.crm_lead_id")
    quotation_reference = fields.Char(string="Reference", related="so_id.quotation_reference")
    quotation_sale_many_ids = fields.Many2many('cyb.quotation', string="Quotation ID",
                                               store=True)
    currency_id = fields.Many2one(related='so_id.currency_id', depends=['so_id.currency_id'], store=True, string='Currency', readonly=True)
    ks_global_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                               string='Overall Discount Type',
                                               readonly=True,)
    ks_global_discount_rate = fields.Float('Overall Discount Rate',
                                           readonly=True)
    ks_amount_discount = fields.Monetary(string='Overall Discount', readonly=True)


    @api.model
    def default_get(self, default_fields):
        res = super(InquiryInvoice, self).default_get(default_fields)
        data = self.env['cyb.quotation'].browse(self._context.get('active_ids', []))
        update = []
        quotation_ids = []
        for rec in data:
            quotation_ids.append(rec.id)
            for record in rec.order_line:
                if record.product_id:
                    update.append((0, 0, {
                        'brand_id': record.brand_id.id,
                        'product_id': record.product_id.id,
                        # 'product_uom': record.product_uom.id,
                        'order_id': record.order_id.id,
                        'name': record.name,
                        'product_uom_qty': record.product_uom_qty,
                        'bonus_quantity': record.bonus_quantity,
                        'price_unit': record.price_unit,
                        'price_subtotal': record.price_subtotal,
                        'price_total': record.price_total,
                        'qty_delivered': record.qty_delivered,
                        'qty_invoiced': record.qty_invoiced,
                        'tax_id': record.tax_id.ids,
                        'remarks': record.remarks,
                        'discount': record.discount,
                        'prod_total_discount': record.prod_total_discount,
                        'pro_available': record.pro_available,
                    }))
        res.update({'new_order_line_ids': update,
                    'quotation_sale_many_ids': quotation_ids,
                    'ks_global_discount_type': data[0].ks_global_discount_type,
                    'ks_global_discount_rate': data[0].ks_global_discount_rate,
                    'ks_amount_discount': data[0].ks_amount_discount,
                    'so_id': self._context.get('active_id'),
                    'partner_id': data.partner_id[0].id})
        return res

    def action_create_quotation_order(self):
        self.ensure_one()
        value = []
        for data in self.new_order_line_ids:
            if data.product_id:
                value.append([0, 0, {
                    # 'display_type': False,
                    'brand_id': data.brand_id.id,
                    'product_id': data.product_id.id,
                    # 'product_uom': data.product_uom.id,
                    'order_id': data.order_id.id,
                    'name': data.name,
                    'product_uom_qty': data.product_uom_qty,
                    'bonus_quantity': data.bonus_quantity,
                    'price_unit': data.price_unit,
                    'tax_id': data.tax_id.ids,
                    'price_subtotal': data.price_subtotal,
                    'price_total': data.price_total,
                    'remarks': data.remarks,
                    'qty_delivered': data.qty_delivered,
                    'qty_invoiced': data.qty_invoiced,
                    'discount': data.discount,
                    'prod_total_discount': data.prod_total_discount,
                    'pro_available': data.pro_available,

                }])
        sale_order = {
            'partner_id': self.partner_id.id,
            # 'inquiry_type': self.inquiry_type,
            # 'ref_id': self.ref_id,
            # 'notes': self.notes,
            # 'so_id': self.so_id.id,
            'order_line': value,
            'ks_global_discount_type': self[0].ks_global_discount_type,
            'ks_global_discount_rate': self[0].ks_global_discount_rate,
            'ks_amount_discount': self[0].ks_amount_discount,
            'quotation_sale_many_ids': self.quotation_sale_many_ids.ids

            # 'state': 'draft',
        }
        so = self.env['sale.order'].create(sale_order)
        so.state = 'sale'
        for i in self.quotation_sale_many_ids:
            a = i.sale_quotation_ids.ids
            a.append(so.id)
            i.update({'sale_quotation_ids': a})
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.order",
            "name": "Quotation",
            "views": [[False, "form"]],
            "res_id": so.id
        }


class GetQuotationorderdata(models.TransientModel):
    _name = 'getsale.quotation'
    _description = "Get Sale Order Data"

    new_order_line_id = fields.Many2one('quotation.wizard')
    name = fields.Char(string="Description")
    product_id = fields.Many2one('product.product', string="Product")
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    bonus_quantity = fields.Float(string='Bonus Qty',   default=1.0)
    order_id = fields.Many2one('cyb.quotation', string='Order Reference', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    price_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
    tax_id = fields.Many2many('account.tax', string='Taxes %', )
    qty_delivered = fields.Float(string='Delivered')
    qty_invoiced = fields.Float(string='Invoiced')
    remarks = fields.Text(string="Remarks")
    price_total = fields.Monetary(string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    discount = fields.Float(string='Discount %', digits='Discount', default=0.0)
    prod_total_discount = fields.Float('Disc. Amount', readonly=True, store=True)
    pro_available = fields.Float(string="Product Available")


    # display_type = fields.Selection([
    #     ('line_section', "Section"),
    #     ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    # discount = fields.Float('Disc.%')

    @api.depends('product_uom_qty', 'price_unit')
    def _compute_total(self):
        for record in self:
            record.price_subtotal = record.product_uom_qty * record.price_unit
