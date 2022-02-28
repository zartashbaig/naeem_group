# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class createsaleorder(models.TransientModel):
    _name = 'create.saleorder'
    _description = "Create Sale Order"

    new_order_line_ids = fields.One2many('getsale.orderdata', 'new_order_line_id', string="Order Line")
    partner_id = fields.Many2one('res.partner', string='Customer', store=True,readonly=True)
    date_Expiration = fields.Date(string="Expiration", related="so_id.date_Expiration")
    date_order = fields.Datetime(string='Order Date', readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    so_id = fields.Many2one('cyb.inquiry', string="Inquiry ID", default="", store=True)
    inquirymany_id = fields.Many2many('cyb.inquiry', string="Inquiry ID", default="", store=True)
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead", related="so_id.crm_lead_id", store=True, readonly=True)
    date_inquiry = fields.Datetime(string="Inquiry Date", related="so_id.date_inquiry", store=True)
    ref_id = fields.Char(string="Document No.", store=True, readonly=True)
    # currency_id = fields.Many2one(related='so_id.currency_id', depends=['so_id.currency_id'], store=True, string='Currency', readonly=True)
    supplier_name = fields.Many2one('res.partner', string="Supplier Name", readonly=True)
    inquiry_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Inquiry Type", readonly=True, store=True)
    notes = fields.Text(string="Remarks", store=True, readonly=True)
    currency_id = fields.Many2one('res.currency', store=True, string='Currency', readonly=True)
    cyb_payment_id = fields.Many2one('account.payment.term', string='Payment term', readonly=True)
    cyb_quotation_id = fields.Many2one('sale.order.template', string='Quotation', readonly=True)
    ks_global_discount_type = fields.Selection([('percent', 'Percentage'), ('amount', 'Amount')],
                                               string='Overall Discount Type',
                                               readonly=True,)
    ks_global_discount_rate = fields.Float('Overall Discount Rate',
                                           readonly=True)
    ks_amount_discount = fields.Monetary(string='Overall Discount', readonly=True)
    user_id = fields.Many2one(
        'res.users', string='Sales Manager', index=True, readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist', readonly=True)


    @api.model
    def default_get(self, default_fields):
        res = super(createsaleorder, self).default_get(default_fields)
        data = self.env['cyb.inquiry'].browse(self._context.get('active_ids', []))
        # customers = data.mapped('partner_id')
        # if customers.__len__()>0:
        #     raise ValidationError('You can not create quotation of multiple inquiries if the customer is not same.')
        update = []
        inquiry_ids = []
        for rec in data:
            inquiry_ids.append(rec.id)
            for record in rec.order_line:
                if record.product_id:
                    update.append((0, 0, {
                        'brand_id': record.brand_id.id,
                        'product_id': record.product_id.id,
                        'product_uom': record.product_uom.id,
                        'order_id': record.order_id.id,
                        'name': record.name,
                        'product_uom_qty': record.product_uom_qty,
                        'price_unit': record.price_unit,
                        'price_subtotal': record.price_subtotal,
                        'price_total': record.price_total,
                        'qty_delivered': record.qty_delivered,
                        'qty_invoiced': record.qty_invoiced,
                        'remarks': record.remarks,
                        'tax_id': record.tax_id.ids,
                        'discount': record.discount,
                        'prod_total_discount': record.prod_total_discount,
                        'pro_available': record.pro_available,
                    }))
        res.update({'new_order_line_ids': update,
                    'partner_id': data.partner_id[0].id,
                    'inquirymany_id': inquiry_ids,
                    'inquiry_type': data[0].inquiry_type,
                    'supplier_name': data[0].supplier_name.id,
                    'cyb_payment_id': data[0].cyb_payment_id.id,
                    'cyb_quotation_id': data[0].cyb_quotation_id.id,
                    'user_id': data[0].user_id.id,
                    'pricelist_id': data[0].pricelist_id.id,
                    'currency_id': data[0].currency_id.id,
                    'ref_id': data[0].ref_id,
                    'crm_lead_id': data.crm_lead_id.id,
                    'ks_global_discount_type': data[0].ks_global_discount_type,
                    'ks_global_discount_rate': data[0].ks_global_discount_rate,
                    'ks_amount_discount': data[0].ks_amount_discount,
                    'so_id': self._context.get('active_id')})
        return res

    def action_create_sale_order(self):
        self.ensure_one()
        value = []
        for data in self.new_order_line_ids:
            if data.product_id:
                value.append([0, 0, {
                    # 'display_type': False,
                    'brand_id': data.brand_id.id,
                    'product_id': data.product_id.id,
                    'product_uom': data.product_uom.id,
                    'order_id': data.order_id.id,
                    'name': data.name,
                    'product_uom_qty': data.product_uom_qty,
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
            'inquiry_type': self[0].inquiry_type,
            'quotation_reference': self[0].ref_id,
            'quotation_new_id': self[0].cyb_quotation_id.id,
            'notes': self.notes,
            'currency_id': self.currency_id.id,
            'date_quotation': self[0].date_inquiry,
            'quotation_payment_id': self[0].cyb_payment_id.id,
            'crm_lead_id': self.crm_lead_id.id,
            'pricelist_id': self[0].pricelist_id.id,
            'order_line': value,
            'ks_global_discount_type': self[0].ks_global_discount_type,
            'ks_global_discount_rate': self[0].ks_global_discount_rate,
            'ks_amount_discount': self[0].ks_amount_discount,
            'state': 'draft',
            'inquirymany_id': self.inquirymany_id.ids
        }
        quotation = self.env['cyb.quotation'].create(sale_order)
        for i in self.inquirymany_id:
            a = i.quotation_many_ids.ids
            a.append(quotation.id)
            i.update({'quotation_many_ids': a})
        return {
            "type": "ir.actions.act_window",
            "res_model": "cyb.quotation",
            "name": "Quotation",
            "views": [[False, "form"]],
            "res_id": quotation.id
        }


class Getsaleorderdata(models.TransientModel):
    _name = 'getsale.orderdata'
    _description = "Get Sale Order Data"

    new_order_line_id = fields.Many2one('create.saleorder')
    name = fields.Text(string="Description", compute='_compute_product_description', store=True)
    product_id = fields.Many2one('product.product', string="Product")
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    # date_planned = fields.Datetime(string='Scheduled Date', default=datetime.today())
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('cyb.inquiry', string='Order Reference', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    price_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
    tax_id = fields.Many2many('account.tax', string='Taxes %',
                              domain=['|', ('active', '=', False), ('active', '=', True)])
    qty_delivered = fields.Float(string='Delivered')
    qty_invoiced = fields.Float(string='Invoiced')
    remarks = fields.Text(string="Remarks")
    price_total = fields.Monetary(string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True)
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

    def _compute_product_description(self):
        for rec in self:
            if rec.product_id:
                rec.name = str([rec.product_id.default_code]) + ' ' + str(rec.product_id.name) + str(
                    rec.product_id.description_sale)


