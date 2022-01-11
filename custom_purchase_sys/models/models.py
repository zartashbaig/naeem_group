# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class CybPurchase(models.Model):
    _name = 'cyb.purchase'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'customer purchase'

    name = fields.Char(string='Purchase Reference', store=True, required=True, readonly=True,
                        default='P')

    partner_id = fields.Many2one(
        'res.partner', string='Customer Name', readonly=True,
        states={'draft': [('readonly', False)]},
        required=True, change_default=True, index=True)
    supplier_name = fields.Many2one('res.partner', string="Supplier Name")
    ref_id = fields.Char(string="Reference")
    # cyb_quotation_id = fields.Many2one('sale.order.template', string='Quotation')
    cyb_payment_id = fields.Many2one('account.payment.term', string='Payment term')
    date_Expiration = fields.Date(string="Expiration")
    date_inquiry = fields.Datetime(string="Purchase Date")
    date_order = fields.Datetime(string='Order Date', readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead')
    inquiry_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Purchase Type")
    notes = fields.Text(string="Remarks")
    cancel = fields.Boolean(string='Cancel')
    user_id = fields.Many2one(
        'res.users', string='Purchase Manager', index=True, tracking=2, default=lambda self: self.env.user)
    order_line = fields.One2many('cyb.product.purchase', 'order_id', string='Order line')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    new_quotation_line_id = fields.Many2one('cyb.quotation.purchase')
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
         readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True, readonly=False)
    purchase_inquiry_many_ids = fields.Many2many('cyb.quotation.purchase', string="Purchase Inquiry ID", default="", store=True)


    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('Cancelled', 'Cancelled')], default='draft', string="Status")

    def action_inquiry_cancel(self):
        self.state = 'Cancelled'

    def action_inquiry_confirm(self):
        self.state = 'confirm'

    @api.model
    def create(self, vals):
        if vals.get('name', 'P') == 'P':
            vals['name'] = self.env['ir.sequence'].next_by_code('cyb.purchase') or "P"
        result = super(CybPurchase, self).create(vals)
        return result

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=5)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)
    total_qty = fields.Float(string='Total QTY', store=True, readonly=True, compute='_amount_all_qty', tracking=4)

    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        for order in self:
            amount_untaxed = amount_tax = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
            order.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
            })

    @api.depends('order_line.product_qty')
    def _amount_all_qty(self):
        """
        Compute the total Quantity of the SO.
        """
        for order in self:
            total_qty = 0
            for line in order.order_line:
                if line.product_id:
                    total_qty += line.product_qty
            order.update({
                'total_qty': total_qty,
            })

    def action_automatic_entry(self):
        action = self.env['ir.actions.act_window']._for_xml_id('custom_purchase_sys.action_quotation_main_transientmodel_wizard')
        update = []
        for order in self:
            for record in order.order_line:
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
                        'qty_received': record.qty_received,
                        'qty_invoiced': record.qty_invoiced,
                        'remarks': record.remarks,
                        'taxes_id': record.taxes_id.ids,
                        # 'discount': record.discount,
                    }))
        # Force the values of the move line in the context to avoid issues
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'create.inquiry.order'
        action['context'] = ctx
        return action


class CybSpecialist(models.Model):
    _name = 'cyb.product.purchase'
    _description = 'product inquiry information'

    name = fields.Text(string="Description", compute='_compute_product_description')
    product_id = fields.Many2one('product.product', string='Product')
    product_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('cyb.purchase', string='Purchase id', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    qty_received = fields.Float(string='Delivered')
    qty_invoiced = fields.Float(string='Invoiced')
    taxes_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')

    remarks = fields.Text(string="Remarks")
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.product_qty > 0:
                taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty,
                                                  product=line.product_id)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })

            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.taxes_id.invalidate_cache(['invoice_repartition_line_ids'], [line.taxes_id.id])

    @api.onchange('price_unit', 'product_qty')
    def onchange_inquiry(self):
        self.price_subtotal = self.product_qty * self.price_unit

    @api.onchange('product_id')
    def onchange_cyb_product_id(self):
        if self.product_id:
            if self.product_id.list_price:
                self.price_unit = self.product_id.list_price

    def _compute_product_description(self):
        for rec in self:
            if rec.product_id:
                rec.name = str([rec.product_id.default_code]) + ' ' + str(rec.product_id.name) + str(rec.product_id.description_sale)



