# -*- coding: utf-8 -*-

import logging
from datetime import datetime

from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)
from odoo import api, fields, models, _


class SaleOrderExt(models.Model):
    _inherit = "sale.order"

    quotation_sale_many_ids = fields.Many2many('cyb.quotation', 'cyb_quotation_rel', string='Quotation Lines')


class CybQuotation(models.Model):
    _name = 'cyb.quotation'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = 'customer quotation'

    name = fields.Char(string='Quotation Reference', store=True,  readonly=True,
                       default='Quo')
    partner_id = fields.Many2one(
        'res.partner', string='Customer', readonly=True,
        states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
         change_default=True, index=True)
    quotation_reference = fields.Char(string='Reference')
    quotation_new_id = fields.Many2one('sale.order.template', string='Quotation Template')
    quotation_payment_id = fields.Many2one('account.payment.term', string='Payment term')
    quotation_Expiration = fields.Date(string="Expiration")
    date_quotation = fields.Datetime(string="Quotation Date")
    order_line = fields.One2many('create.quotation.friend', 'order_id', string='Order line')
    company_id = fields.Many2one('res.company', 'Company',  index=True,
                                 default=lambda self: self.env.company)
    date_order = fields.Datetime(string='Order Date',  readonly=True, index=True,
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, copy=False,
                                 default=fields.Datetime.now,
                                 help="Creation date of draft/sent orders,\nConfirmation date of confirmed orders.")
    crm_lead_id = fields.Many2one('crm.lead', string="CRM Lead")
    inquiry_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Inquiry Type")
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
    inquirymany_id = fields.Many2many('cyb.inquiry','inquiry_rel', string='Inquiry List')
    sale_quotation_ids = fields.Many2many('sale.order', string='Sale List')

    def action_quotation_cancel(self):
        self.state = 'Cancelled'

    def action_quotation_confirm(self):
        self.state = 'confirm'

    @api.model
    def create(self, vals):
        if vals.get('name', 'Quo') == 'Quo':
            vals['name'] = self.env['ir.sequence'].next_by_code('cyb.quotation') or "Quo"
        result = super(CybQuotation, self).create(vals)
        return result

    # def action_quotation_email(self):
    #     print('email is....')
    #     inquiry_template_id = self.env.ref('inquiry_cyb.inquiry_email_template').id
    #     self.env['mail.template'].browse(inquiry_template_id).send_mail(self.id, force_send=True)
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
         readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")
    currency_id = fields.Many2one(related='pricelist_id.currency_id', depends=["pricelist_id"], store=True,
                                  readonly=False)

    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all',
                                     tracking=5)
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', tracking=4)

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

    def action_create_so(self):
        action = self.env['ir.actions.act_window']._for_xml_id('inquiry_cyb.inquiry_invoice_wizard')
        update = []
        for order in self:
            for record in order.order_line:
                if record.product_id:
                    update.append((0, 0, {
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
                        # 'discount': record.discount,
                    }))

        # Force the values of the move line in the context to avoid issues
        ctx = dict(self.env.context)
        ctx.pop('active_id', None)
        ctx['active_ids'] = self.ids
        ctx['active_model'] = 'getsale.quotation'
        action['context'] = ctx
        return action


class QuotationFriends(models.Model):
    _name = 'create.quotation.friend'
    _description = 'quotation'

    name = fields.Char(string="Description")
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float(string='Quantity', digits='Product Unit of Measure',  default=1.0)
    qty_delivered = fields.Float(string='Delivered')
    qty_invoiced = fields.Float(string='Invoiced')
    price_unit = fields.Float(string='Unit price')
    # price_subtotal = fields.Float(string="Subtotal")
    tax_id = fields.Many2many('account.tax', string='Taxes',
                              domain=['|', ('active', '=', False), ('active', '=', True)])

    product_uom = fields.Many2one('uom.uom', string='Product Unit of Measure')

    order_id = fields.Many2one('cyb.quotation', string='Quotation id', ondelete='cascade', index=True)
    remarks = fields.Text(string="Remarks")

    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True,
                                  string='Currency', readonly=True)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)

    @api.depends('product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            if line.product_uom_qty > 0:
                taxes = line.tax_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_uom_qty,
                                                product=line.product_id)
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

