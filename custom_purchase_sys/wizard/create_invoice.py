# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class createsaleorder(models.TransientModel):
    _name = 'create.inquiry.order'
    _description = "Create Purchase Inquiry"

    new_order_line_ids = fields.One2many('getpurchase.orderdata', 'new_order_line_id', string="Order Line")
    partner_id = fields.Many2one('res.partner', string='Customer', store=True, readonly=True)
    date_Expiration = fields.Date(string="Expiration", related="so_id.date_Expiration")
    date_order = fields.Datetime(string='Order Date', readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    so_id = fields.Many2one('cyb.purchase', string="Purchase Inquiry ID", default="", store=True)
    purchase_inquirymany_id = fields.Many2many('cyb.purchase', string="Purchase Inquiry ID", default="", store=True)
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead", related="so_id.crm_lead_id", store=True)
    date_inquiry = fields.Datetime(string="Purchase Date", related="so_id.date_inquiry", store=True)
    ref_id = fields.Char(string="Reference", related="so_id.ref_id", store=True)
    inquiry_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Purchase Type", related="so_id.inquiry_type", store=True)
    notes = fields.Text(string="Remarks", related="so_id.notes", store=True)

    @api.model
    def default_get(self, default_fields):
        res = super(createsaleorder, self).default_get(default_fields)
        data = self.env['cyb.purchase'].browse(self._context.get('active_ids', []))
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
                        'product_qty': record.product_qty,
                        'price_unit': record.price_unit,
                        'price_subtotal': record.price_subtotal,
                        'price_total': record.price_total,
                        'qty_received': record.qty_received,
                        'qty_invoiced': record.qty_invoiced,
                        'remarks': record.remarks,
                        'taxes_id': record.taxes_id.ids,
                    }))
        res.update({'new_order_line_ids': update,
                    'partner_id': data.partner_id[0].id,
                    'purchase_inquirymany_id': inquiry_ids,
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
                    'product_qty': data.product_qty,
                    'price_unit': data.price_unit,
                    'taxes_id': data.taxes_id.ids,
                    'price_subtotal': data.price_subtotal,
                    'price_total': data.price_total,
                    'remarks': data.remarks,
                    'qty_received': data.qty_received,
                    'qty_invoiced': data.qty_invoiced,
                }])

        sale_order = {
            'partner_id': self.partner_id.id,
            'inquiry_type': self.inquiry_type,
            'ref_id': self.ref_id,
            'notes': self.notes,
            # 'so_id': self.so_id.id,
            'order_line': value,
            'state': 'draft',
            'purchase_inquirymany_id': self.purchase_inquirymany_id.ids
        }
        quotation = self.env['cyb.quotation.purchase'].create(sale_order)
        for i in self.purchase_inquirymany_id:
            a = i.purchase_inquiry_many_ids.ids
            a.append(quotation.id)
            i.update({'purchase_inquiry_many_ids': a})
        return {
            "type": "ir.actions.act_window",
            "res_model": "cyb.quotation.purchase",
            "name": "Quotation",
            "views": [[False, "form"]],
            "res_id": quotation.id
        }


class Getsaleorderdata(models.TransientModel):
    _name = 'getpurchase.orderdata'
    _description = "Get Sale Order Data"

    new_order_line_id = fields.Many2one('create.inquiry.order')
    name = fields.Text(string="Description", compute='_compute_product_description', store=True)
    product_id = fields.Many2one('product.product', string="Product")
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    # date_planned = fields.Datetime(string='Scheduled Date', default=datetime.today())
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('cyb.purchase', string='Order Reference', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    price_subtotal = fields.Float(string="Sub Total", compute='_compute_total')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    qty_received = fields.Float(string='Delivered')
    qty_invoiced = fields.Float(string='Invoiced')
    remarks = fields.Text(string="Remarks")
    price_total = fields.Monetary(string='Total', readonly=True, store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True)



    # display_type = fields.Selection([
    #     ('line_section', "Section"),
    #     ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    # discount = fields.Float('Disc.%')

    @api.depends('product_qty', 'price_unit')
    def _compute_total(self):
        for record in self:
            record.price_subtotal = record.product_qty * record.price_unit

    def _compute_product_description(self):
        for rec in self:
            if rec.product_id:
                rec.name = str([rec.product_id.default_code]) + ' ' + str(rec.product_id.name) + str(
                    rec.product_id.description_sale)

