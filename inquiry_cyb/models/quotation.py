# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class SaleOrderExt(models.Model):
    _inherit = "sale.order"

    quotation_sale_many_ids = fields.Many2many('cyb.quotation', 'cyb_quotation_rel', string='Quotation Lines')
    count = fields.Integer(compute="_compute_discount_total", string='SN (Total)', store=True, readonly=1)
    total_qty = fields.Float(string='Total QTY', store=True, readonly=True, compute='_amount_all_qty', tracking=4)
    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        string="Discount %",
        currency_field="currency_id",
        store=True, digits=(16, 4)
    )
    name = fields.Char(string='Order Reference', required=True, copy=False, readonly=True,
                       states={'draft': [('readonly', False)]}, index=True, default=lambda self: _('SO'))
    inquiry_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Inquiry Type", default='STOCKIEST')
    p_apply = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="P.Price Apply", default='no')
    ref_id = fields.Char(string="Document No.")
    account_num = fields.Char(string="Account No.")
    credit_lim = fields.Float(string="Credit Limit", digits=(16, 4))
    d_date = fields.Date(string="Delivery Date",)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=False)
    manager_id = fields.Many2one('res.partner', string="Sales Manager")
    remarks = fields.Text(string="Remarks")
    cancel = fields.Boolean(string='Cancel')
    net_amount = fields.Float(string='Net Amount', readonly=True, store=True, digits=(16, 4))
    taxes_check = fields.Selection([
        ('With_Tax', 'With Tax'),
        ('Without_Tax', 'Without Tax')
    ], string="With Tax / Without Tax")
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead")


    @api.model
    def create(self, vals):
        if 'company_id' in vals:
            self = self.with_company(vals['company_id'])
        if vals.get('name', _('SO')) == _('SO'):
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self.env['ir.sequence'].next_by_code('sale.order', sequence_date=seq_date) or _('SO')

        # Makes sure partner_invoice_id', 'partner_shipping_id' and 'pricelist_id' are defined
        if any(f not in vals for f in ['partner_invoice_id', 'partner_shipping_id', 'pricelist_id']):
            partner = self.env['res.partner'].browse(vals.get('partner_id'))
            addr = partner.address_get(['delivery', 'invoice'])
            vals['partner_invoice_id'] = vals.setdefault('partner_invoice_id', addr['invoice'])
            vals['partner_shipping_id'] = vals.setdefault('partner_shipping_id', addr['delivery'])
            vals['pricelist_id'] = vals.setdefault('pricelist_id', partner.property_product_pricelist.id)
        result = super(SaleOrderExt, self).create(vals)
        return result

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

    @api.onchange('quotation_sale_many_ids')
    def quotation_lines_append(self):
        self.ensure_one()
        value = []
        for data in self.quotation_sale_many_ids.order_line:
            for merger in self.order_line:
                if data.product_id.id == merger.product_id.id:
                    merger.product_uom_qty += data.product_uom_qty
                else:
                    if data.product_id:
                        value.append([0, 0, {
                            'display_type': False,
                            'brand_id': data.brand_id.id,
                            'product_id': data.product_id.id,
                            'product_uom': data.product_uom.id,
                            'order_id': data.order_id.id,
                            'name': data.name,
                            'product_uom_qty': data.product_uom_qty,
                            'bonus_quantity': data.bonus_quantity,
                            'price_unit': data.price_unit,
                            'price_subtotal': data.price_subtotal,
                            'qty_delivered': data.qty_delivered,
                            'qty_invoiced': data.qty_invoiced,
                            'remarks': data.remarks,
                            'tax_id': data.tax_id.ids,
                            'discount': data.discount,
                            'prod_total_discount': data.prod_total_discount,
                            'pro_available': data.pro_available,
                        }])
                    if not data.product_id:
                        if data.display_type == 'line_section':
                            value.append((0, 0, {
                                'display_type': 'line_section',
                                'brand_id': data.brand_id.id,
                                'product_id': data.product_id.id,
                                'product_uom': data.product_uom.id,
                                'order_id': data.order_id.id,
                                'name': data.name,
                                'product_uom_qty': data.product_uom_qty,
                                'bonus_quantity': data.bonus_quantity,
                                'price_unit': data.price_unit,
                                'price_subtotal': data.price_subtotal,
                                'qty_delivered': data.qty_delivered,
                                'qty_invoiced': data.qty_invoiced,
                                'remarks': data.remarks,
                                'tax_id': data.tax_id.ids,
                                'discount': data.discount,
                                'prod_total_discount': data.prod_total_discount,
                                'pro_available': data.pro_available,
                            }))
                        elif data.display_type == 'line_note':
                            value.append((0, 0, {
                                'display_type': 'line_note',
                                'brand_id': data.brand_id.id,
                                'product_id': data.product_id.id,
                                'product_uom': data.product_uom.id,
                                'order_id': data.order_id.id,
                                'name': data.name,
                                'product_uom_qty': data.product_uom_qty,
                                'bonus_quantity': data.bonus_quantity,
                                'price_unit': data.price_unit,
                                'price_subtotal': data.price_subtotal,
                                'qty_delivered': data.qty_delivered,
                                'qty_invoiced': data.qty_invoiced,
                                'remarks': data.remarks,
                                'tax_id': data.tax_id.ids,
                                'discount': data.discount,
                                'prod_total_discount': data.prod_total_discount,
                                'pro_available': data.pro_available,
                            }))
            quotation_order = {
                'order_line': value,
            }
            qo_main = self.write(quotation_order)
        # return True
        # return {
        #     "res_id": qo_main
        # }


class SaleOrderLineExt(models.Model):
    _inherit = "sale.order.line"

    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    remarks = fields.Text(string="Remarks")
    hs_code = fields.Char(string="HS Code")
    wh_id = fields.Many2one('stock.warehouse', string="Ware House")
    bonus_quantity = fields.Float(string='Bonus Qty', default=1.0)
    tax_amount = fields.Float(string="Tax Amount",compute="_tax_amount_compute", digits=(16, 4))
    prod_total_discount = fields.Float('Disc. Amount', readonly=True, store=True, digits=(16, 4))
    pro_available = fields.Float(related='product_id.qty_available', string="Product Available")
    tax_id = fields.Many2many('account.tax', string='Taxes %',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    def product_qty_location_check(self):
        for rec in self:
            if rec.product_id:
                rec.pro_available = rec.product_id.qty_available

    @api.onchange('price_unit', 'product_uom_qty', 'tax_id')
    def _tax_amount_compute(self):
        for rec in self:
            tax_amount = 0
            if rec.price_unit:
                for tax in rec.tax_id:
                    tax_amount += rec.price_unit * rec.product_uom_qty * tax.amount / 100
                rec.tax_amount = tax_amount
            else:
                rec.tax_amount = 0.0

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.product_uom_qty > 0:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id)
                total_prod_price = line.product_uom_qty * line.price_unit
                prod_total_discount = total_prod_price*(line.discount / 100)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                    'prod_total_discount': prod_total_discount,
                })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])


class CybQuotation(models.Model):
    _name = 'cyb.quotation'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'customer quotation'

    name = fields.Char(string='Quotation Reference', store=True, readonly=True,
                       default='SQUO')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        change_default=True, index=True)
    quotation_reference = fields.Char(string='Document No.')
    quotation_new_id = fields.Many2one('sale.order.template', string='Quotation Template')
    quotation_payment_id = fields.Many2one('account.payment.term', string='Payment term')
    manager_id = fields.Many2one('res.user', string='Sale Manager')
    quotation_Expiration = fields.Date(string="Expiration")
    date_quotation = fields.Datetime(string="Document Date")
    order_line = fields.One2many('create.quotation.friend', 'order_id', string='Order line')
    company_id = fields.Many2one('res.company', 'Company', index=True,
                                 default=lambda self: self.env.company)
    date_order = fields.Datetime(string='Order Date', readonly=True, index=True,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    cancel = fields.Boolean(string='cancel')
    inquiry_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Sale Quotation Type")
    p_apply = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No')
    ], string="Is Product Price Apply", default='no')
    ref_id = fields.Char(string="Inquiry Reference No")
    notes = fields.Text(string="Remarks")

    user_id = fields.Many2one(
        'res.users', string='Salesperson', index=True, tracking=2, default=lambda self: self.env.user,
        domain=lambda self: [('groups_id', 'in', self.env.ref('sales_team.group_sale_salesman').id)])
    team_id = fields.Many2one(
        'crm.team', 'Sales Team', )

    state = fields.Selection(
        [('draft', 'Draft'),
         ('confirm', 'Confirmed'),
         ('Cancelled', 'Cancelled')], default='draft', string="Status")
    notes_qut = fields.Text('Remarks')
    inquirymany_id = fields.Many2many('cyb.inquiry', string='Inquiry List')
    sale_quotation_ids = fields.Many2many('sale.order', string='Sale List')
    taxes_check = fields.Selection([
        ('With_Tax', 'With Tax'),
        ('Without_Tax', 'Without Tax')
    ], string="With Tax / Without Tax")

    def action_quotation_cancel(self):
        self.state = 'Cancelled'

    def action_quotation_confirm(self):
        self.state = 'confirm'

    def action_quotation_reset(self):
        self.state = 'draft'

    @api.model
    def create(self, vals):
        if vals.get('name', 'SQUO') == 'SQUO':
            vals['name'] = self.env['ir.sequence'].next_by_code('cyb.quotation') or "SQUO"
        result = super(CybQuotation, self).create(vals)
        return result

    # def action_quotation_email(self):
    #     print('email is....')
    #     inquiry_template_id = self.env.ref('inquiry_cyb.inquiry_email_template').id
    #     self.env['mail.template'].browse(inquiry_template_id).send_mail(self.id, force_send=True)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True,
                                  readonly=False)

    amount_untaxed = fields.Monetary(string='Total Excl ST Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=5, digits=(16, 4))
    amount_tax = fields.Monetary(string='Total Taxation Amount', store=True, readonly=True, compute='_amount_all', digits=(16, 4))
    amount_total = fields.Monetary(string='Total Incl ST Amount', store=True, readonly=True, compute='_amount_all',
                                   tracking=4, digits=(16, 4))
    count = fields.Integer(compute="_compute_discount_total", string='SN (Total)', store=True, readonly=1)
    total_qty = fields.Float(string='Total QTY', store=True, readonly=True, compute='_amount_all_qty', tracking=4)
    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        string="Discount %",
        currency_field="currency_id",
        store=True, digits=(16, 4)
    )
    net_amount = fields.Float(string='Net Amount', readonly=True, store=True, digits=(16, 4))

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
                total_qty += line.product_uom_qty
            order.update({
                'total_qty': total_qty,
            })

    def action_create_so(self):
        action = self.env['ir.actions.act_window']._for_xml_id('inquiry_cyb.inquiry_invoice_wizard')
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
                        'bonus_quantity': record.bonus_quantity,
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
                            'bonus_quantity': record.bonus_quantity,
                            'price_unit': record.price_unit,
                            'price_subtotal': record.price_subtotal,
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
                            'bonus_quantity': record.bonus_quantity,
                            'price_unit': record.price_unit,
                            'price_subtotal': record.price_subtotal,
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
        ctx['active_model'] = 'getsale.quotation'
        action['context'] = ctx
        return action

    @api.onchange('inquirymany_id')
    def quotation_lines_append(self):
        self.ensure_one()
        value = []
        for data in self.inquirymany_id.order_line:
            for merger in self.order_line:
                if data.product_id.id == merger.product_id.id:
                    merger.product_uom_qty += data.product_uom_qty
                else:
                    if data.product_id:
                        value.append([0, 0, {
                            'display_type': False,
                            'brand_id': data.brand_id.id,
                            'product_id': data.product_id.id,
                            'product_uom': data.product_uom.id,
                            'order_id': data.order_id.id,
                            'name': data.name,
                            'product_uom_qty': data.product_uom_qty,
                            'bonus_quantity': data.bonus_quantity,
                            'price_unit': data.price_unit,
                            'price_subtotal': data.price_subtotal,
                            'qty_delivered': data.qty_delivered,
                            'qty_invoiced': data.qty_invoiced,
                            'remarks': data.remarks,
                            'tax_id': data.tax_id.ids,
                            'discount': data.discount,
                            'prod_total_discount': data.prod_total_discount,
                            'pro_available': data.pro_available,
                        }])
                    if not data.product_id:
                        if data.display_type == 'line_section':
                            value.append((0, 0, {
                                'display_type': 'line_section',
                                'brand_id': data.brand_id.id,
                                'product_id': data.product_id.id,
                                'product_uom': data.product_uom.id,
                                'order_id': data.order_id.id,
                                'name': data.name,
                                'product_uom_qty': data.product_uom_qty,
                                'bonus_quantity': data.bonus_quantity,
                                'price_unit': data.price_unit,
                                'price_subtotal': data.price_subtotal,
                                'qty_delivered': data.qty_delivered,
                                'qty_invoiced': data.qty_invoiced,
                                'remarks': data.remarks,
                                'tax_id': data.tax_id.ids,
                                'discount': data.discount,
                                'prod_total_discount': data.prod_total_discount,
                                'pro_available': data.pro_available,
                            }))
                        elif data.display_type == 'line_note':
                            value.append((0, 0, {
                                'display_type': 'line_note',
                                'brand_id': data.brand_id.id,
                                'product_id': data.product_id.id,
                                'product_uom': data.product_uom.id,
                                'order_id': data.order_id.id,
                                'name': data.name,
                                'product_uom_qty': data.product_uom_qty,
                                'bonus_quantity': data.bonus_quantity,
                                'price_unit': data.price_unit,
                                'price_subtotal': data.price_subtotal,
                                'qty_delivered': data.qty_delivered,
                                'qty_invoiced': data.qty_invoiced,
                                'remarks': data.remarks,
                                'tax_id': data.tax_id.ids,
                                'discount': data.discount,
                                'prod_total_discount': data.prod_total_discount,
                                'pro_available': data.pro_available,
                            }))
            quotation_order = {
                'order_line': value,
            }
            qo_main = self.write(quotation_order)
        # return True
        # return {
        #     "res_id": qo_main
        # }


class QuotationFriends(models.Model):
    _name = 'create.quotation.friend'
    _description = 'quotation'

    name = fields.Text(string="Description")
    product_id = fields.Many2one('product.product', string='Product')
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure', default=1.0)
    bonus_quantity = fields.Float(string='Bonus Qty', default=1.0)
    qty_delivered = fields.Float(string='Delivered')
    qty_invoiced = fields.Float(string='Invoiced')
    price_unit = fields.Float(string='Unit price', digits=(16, 4))
    # price_subtotal = fields.Float(string="Subtotal")
    tax_id = fields.Many2many('account.tax', string='Taxes %',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')

    order_id = fields.Many2one('cyb.quotation', string='Quotation id', ondelete='cascade', index=True)
    remarks = fields.Text(string="Remarks")
    # new fields added by WaqasAli
    wh_id = fields.Many2one('stock.warehouse', string="Ware House")
    hs_code = fields.Char(string="HS code")
    pro_available = fields.Float(related='product_id.qty_available', string="Product Available")
    tax_amount = fields.Float(string="Tax Amount",compute='_tax_amount_compute', digits=(16, 4))

    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True, digits=(16, 4))
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True, digits=(16, 4))
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True, digits=(16, 4))
    discount = fields.Float(string='Discount %', digits='Discount', default=0.0)
    prod_total_discount = fields.Float('Disc. Amount', readonly=True, store=True, digits=(16, 4))
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

    @api.onchange('price_unit', 'product_uom_qty', 'tax_id')
    def _tax_amount_compute(self):
        for rec in self:
            tax_amount = 0
            if rec.price_unit:
                for tax in rec.tax_id:
                    tax_amount += rec.price_unit * rec.product_uom_qty * tax.amount / 100
                rec.tax_amount = tax_amount
            else:
                rec.tax_amount = 0.0

    @api.onchange('price_unit', 'product_uom_qty')
    def onchange_inquiry(self):
        self.price_subtotal = self.product_uom_qty * self.price_unit

    @api.onchange('product_id')
    def onchange_cyb_product_id(self):
        if self.product_id:
            if self.product_id.list_price:
                self.price_unit = self.product_id.list_price

    def _compute_product_description(self):
        for rec in self:
            if rec.product_id:
                rec.name = str([rec.product_id.default_code]) + ' ' + str(rec.product_id.name) + str(rec.product_id.description_sale)

    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
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
                prod_total_discount = total_prod_price*(line.discount / 100)
                line.update({
                    'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'],
                    'prod_total_discount': prod_total_discount,
                })
            if self.env.context.get('import_file', False) and not self.env.user.user_has_groups(
                    'account.group_account_manager'):
                line.tax_id.invalidate_cache(['invoice_repartition_line_ids'], [line.tax_id.id])
