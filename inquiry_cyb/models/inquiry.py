# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _
from odoo.tools.misc import formatLang, get_lang
from odoo.osv import expression
from odoo.tools import float_is_zero, float_compare


class CybInquiry(models.Model):
    _name = 'cyb.inquiry'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'customer inquiry'

    name = fields.Char(string='Inquiry Reference', store=True, required=True, readonly=True,
                       default='SINQ')

    partner_id = fields.Many2one(
        'res.partner', string='Customer Name', readonly=True,
        states={'draft': [('readonly', False)]},
        required=True, change_default=True, index=True)
    supplier_name = fields.Many2one('res.partner', string="Supplier Name")
    ref_id = fields.Char(string="Document No.")
    # pi_num = fields.Char(string="Inquiry No.")
    cyb_quotation_id = fields.Many2one('sale.order.template', string='Quotation')
    cyb_payment_id = fields.Many2one('account.payment.term', string='Payment term')
    date_Expiration = fields.Date(string="Expiration")
    remarks = fields.Text(string="Remarks")
    # manager_id = fields.Many2one('res.user', string='Purchase Manager')
    date_inquiry = fields.Datetime(string="Document Date")
    date_order = fields.Datetime(string='Order Date', readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead')
    inquiry_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Sale Inquiry Type", default='STOCKIEST')
    notes = fields.Text(string="Remarks")
    user_id = fields.Many2one(
        'res.users', string='Sales Manager', index=True, tracking=2, default=lambda self: self.env.user)
    order_line = fields.One2many('cyb.product.inquiry', 'order_id', string='Order line')
    company_id = fields.Many2one('res.company', 'Company', required=True, index=True,
                                 default=lambda self: self.env.company)
    # new_quotation_line_id = fields.Many2one('cyb.quotation')
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True, readonly=False)
    quotation_many_ids = fields.Many2many('cyb.quotation', string="Inquiry ID", default="", store=True)
    taxes_check = fields.Selection([
        ('With_Tax', 'With Tax'),
        ('Without_Tax', 'Without Tax')
    ], string="With Tax / Without Tax")


    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('Cancelled', 'Cancelled')], default='draft', string="Status")

    def action_inquiry_cancel(self):
        self.state = 'Cancelled'

    def action_inquiry_confirm(self):
        self.state = 'confirm'

    def action_inquiry_reset(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('name', 'SINQ') == 'SINQ':
            vals['name'] = self.env['ir.sequence'].next_by_code('cyb.inquiry') or "SINQ"
        result = super(CybInquiry, self).create(vals)
        return result

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=5, digits=(16, 4))
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all', digits=(16, 4))
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4, digits=(16, 4))
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

    @api.depends('order_line.product_uom_qty')
    def _amount_all_qty(self):
        """
        Compute the total Quantity of the SO.
        """
        for order in self:
            total_qty = 0
            for line in order.order_line:
                if line.product_id:
                    total_qty += line.product_uom_qty
            order.update({
                'total_qty': total_qty,
            })

    def action_automatic_entry(self):
        action = self.env['ir.actions.act_window']._for_xml_id('inquiry_cyb.action_transientmodel_wizard')
        update = []
        for order in self:
            for record in order.order_line:
                if record.product_id:
                    update.append((0, 0, {
                        'display_type': False,
                        'brand_id': record.brand_id.id,
                        'product_id': record.product_id.id,
                        'product_uom': record.product_uom.id,
                        'order_id': record.order_id.id,
                        'name': record.name,
                        'product_uom_qty': record.product_uom_qty,
                        'price_unit': record.price_unit,
                        'price_subtotal': record.price_subtotal,
                        'qty_delivered': record.qty_delivered,
                        'qty_invoiced': record.qty_invoiced,
                        'remarks': record.remarks,
                        'tax_id': record.tax_id.ids,
                        'discount': record.discount,
                        'prod_total_discount': record.prod_total_discount,
                        'pro_available': record.pro_available,
                    }))
                else:
                    if record.display_type == 'line_section':
                        update.append([0, 0, {
                            'display_type': 'line_section',
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
                        }])
                    elif record.display_type == 'line_note':
                        update.append([0, 0, {
                            'display_type': 'line_note',
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
                        }])
        # Force the values of the move line in the context to avoid issues
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'create.saleorder'
        action['context'] = ctx
        return action


class CybSpecialist(models.Model):
    _name = 'cyb.product.inquiry'
    _description = 'product inquiry information'

    name = fields.Text(string="Description")
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', required=True, default=1.0)
    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')
    order_id = fields.Many2one('cyb.inquiry', string='inquiry id', ondelete='cascade', index=True)
    price_unit = fields.Float(string='Unit Price', digits='Product Price')
    qty_delivered = fields.Float(string='Delivered')
    qty_invoiced = fields.Float(string='Invoiced')
    tax_id = fields.Many2many('account.tax', string='Taxes %', domain=['|', ('active', '=', False), ('active', '=', True)])
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    remarks = fields.Text(string="Remarks")
    hs_code = fields.Char(string="HS code")
    wh_id = fields.Many2one('stock.warehouse', string="Ware House")
    tax_amount = fields.Float(compute="_tax_amount_compute", string="Tax Amount",  digits=(16, 4))
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency', readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True, digits=(16, 4))
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True, digits=(16, 4))
    pro_available = fields.Float(related='product_id.qty_available', string="Product Available")
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True, digits=(16, 4))
    discount = fields.Float(string='Discount %', digits='Discount', default=0.0, store=True,)
    prod_total_discount = fields.Float('Disc. Amount', store=True, digits=(16, 4))
    display_type = fields.Selection([
        ('line_section', "Section"),
        ('line_note', "Note")], default=False, help="Technical field for UX purpose.")
    partner_id = fields.Many2one(
        'res.partner', string='Customer Name', index=True)

    def _get_computed_name(self):
        self.ensure_one()

        if not self.product_id:
            return ''

        if self.partner_id.lang:
            product = self.product_id.with_context(lang=self.partner_id.lang)
        else:
            product = self.product_id

        values = []
        if product.partner_ref:
            values.append(product.partner_ref)
        # if self.journal_id.type == 'sale':
        if product.description_sale:
            values.append(product.description_sale)
        # elif self.journal_id.type == 'purchase':
        #     if product.description_purchase:
        #         values.append(product.description_purchase)
        return '\n'.join(values)

    @api.onchange('product_id')
    def _onchange_product_id(self):
        for line in self:
            if not line.product_id or line.display_type in ('line_section', 'line_note'):
                continue

            line.name = line._get_computed_name()

    def product_qty_location_check(self):
        for rec in self:
            if rec.product_id:
                rec.pro_available = rec.product_id.qty_available

    @api.depends('price_unit', 'product_uom_qty', 'tax_id')
    def _tax_amount_compute(self):
        for rec in self:
            tax_amount = 0
            if rec.price_unit:
                for tax in rec.tax_id:
                    tax_amount += rec.price_unit * rec.product_uom_qty * tax.amount / 100
                rec.tax_amount = tax_amount
            else:
                rec.tax_amount = 0.0

    # @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    # def _compute_amount(self):
    #     """
    #     Compute the amounts of the SO line.
    #     """
    #     for line in self:
    #         if line.product_uom_qty > 0:
    #             price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
    #             taxes = line.tax_id.compute_all(price, line.price_unit, line.order_id.currency_id, line.product_uom_qty,
    #                                             product=line.product_id)
    #             line.update({
    #                 'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
    #                 'price_total': taxes['total_included'],
    #                 'price_subtotal': taxes['total_excluded'],
    #             })
    #
    #         if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
    #                 'account.group_account_manager'):
    #             line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id', 'prod_total_discount')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.product_uom_qty > 0:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id)
                total_prod_price = line.product_uom_qty*line.price_unit
                prod_total_discount = 0
                discount_perc = 0
                if line.discount:
                    prod_total_discount = total_prod_price * (line.discount / 100)
                    line.update({
                        'prod_total_discount': prod_total_discount,
                    })
                elif line.prod_total_discount:

                    discount_perc = (line.prod_total_discount / total_prod_price) * 100
                    line.update({
                        'discount': discount_perc,
                    })
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])

    @api.onchange('price_unit', 'product_uom_qty')
    def onchange_inquiry(self):
        self.price_subtotal = self.product_uom_qty * self.price_unit

    @api.onchange('product_id')
    def onchange_cyb_product_id(self):
        if self.product_id:
            if self.product_id.list_price:
                self.price_unit = self.product_id.list_price







