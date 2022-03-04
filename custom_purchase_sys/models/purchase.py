# -*- coding: utf-8 -*-

from odoo import api, fields, models


class PurchaseDiscount(models.Model):
    _inherit = "purchase.order"

    name = fields.Char('Order Reference', required=True, index=True, copy=False, default='PO')
    quotation_sale_many_ids = fields.Many2many('cyb.quotation.purchase', string='Quotation Lines')
    currency_id = fields.Many2one('res.currency', string='Currency')
    manager_id = fields.Many2one('res.user', string='Purchase Manager')
    account_id = fields.Many2one('account.account', string='Account')
    customer_id = fields.Many2one('res.partner', string='Customer Name')
    remarks = fields.Text(string="Remarks")
    crm_lead_id = fields.Many2one('crm.lead', string='CRM Lead')
    dc_type = fields.Selection([
        ('STOCKIEST', 'STOCKIEST'),
        ('INDENTING', 'INDENTING')
    ], string="Purchase Type", default='STOCKIEST')

    net_amount = fields.Float(string='Net Amount', readonly=True, store=True)
    count = fields.Integer(compute="_compute_discount_total", string='SN (Total)', store=True, readonly=1)
    total_qty = fields.Float(string='Total QTY', store=True, readonly=True, compute='_amount_all_qty', tracking=4)
    discount_total = fields.Monetary(
        compute="_compute_discount_total",
        string="Discount %",
        currency_field="currency_id",
        store=True,
    )
    pricelist_id = fields.Many2one(
        'product.pricelist', string='Pricelist', check_company=True,  # Unrequired company
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", tracking=1,
        help="If you change the pricelist, only newly added lines will be affected.")

    taxes_check = fields.Selection([
        ('With_Tax', 'With Tax'),
        ('Without_Tax', 'Without Tax')
    ], string="With Tax / Without Tax")

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

    @api.onchange('quotation_sale_many_ids')
    def quotation_lines_append(self):
        self.ensure_one()
        value = []
        for data in self.quotation_sale_many_ids[-1].order_line:
            for merger in self.order_line:
                if data.product_id.id == merger.product_id.id:
                    merger.product_qty += data.product_qty
                else:
                    if data.product_id:
                        value.append([0, 0, {
                            'display_type': False,
                            'brand_id': data.brand_id.id,
                            'product_id': data.product_id.id,
                            'order_id': data.order_id.id,
                            'name': data.name,
                            'product_qty': data.product_qty,
                            # 'bonus_quantity': data.bonus_quantity,
                            'price_unit': data.price_unit,
                            'taxes_id': data.taxes_id.ids,
                            'price_subtotal': data.price_subtotal,
                            'price_total': data.price_total,
                            'remarks': data.remarks,
                            'qty_received': data.qty_received,
                            'qty_invoiced': data.qty_invoiced,
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
                                'order_id': data.order_id.id,
                                'name': data.name,
                                'product_qty': data.product_qty,
                                # 'bonus_quantity': data.bonus_quantity,
                                'price_unit': data.price_unit,
                                'taxes_id': data.taxes_id.ids,
                                'price_subtotal': data.price_subtotal,
                                'price_total': data.price_total,
                                'remarks': data.remarks,
                                'qty_received': data.qty_received,
                                'qty_invoiced': data.qty_invoiced,
                                'discount': data.discount,
                                'prod_total_discount': data.prod_total_discount,
                                'pro_available': data.pro_available,
                            }))
                        elif data.display_type == 'line_note':
                            value.append((0, 0, {
                                'display_type': 'line_note',
                                'brand_id': data.brand_id.id,
                                'product_id': data.product_id.id,
                                'order_id': data.order_id.id,
                                'name': data.name,
                                'product_qty': data.product_qty,
                                # 'bonus_quantity': data.bonus_quantity,
                                'price_unit': data.price_unit,
                                'taxes_id': data.taxes_id.ids,
                                'price_subtotal': data.price_subtotal,
                                'price_total': data.price_total,
                                'remarks': data.remarks,
                                'qty_received': data.qty_received,
                                'qty_invoiced': data.qty_invoiced,
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

    @api.model
    def create(self, vals):
        company_id = vals.get('company_id', self.default_get(['company_id'])['company_id'])
        # Ensures default picking type and currency are taken from the right company.
        self_comp = self.with_company(company_id)
        if vals.get('name', 'PO') == 'PO':
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            vals['name'] = self_comp.env['ir.sequence'].next_by_code('purchase.order', sequence_date=seq_date) or '/'
        return super(PurchaseDiscount, self_comp).create(vals)


class PurchaseLineDiscount(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float('Discount%')
    bonus_quantity = fields.Float(string='Bonus Qty', default=1.0)
    prod_total_discount = fields.Float('Disc. Amount', readonly=True, store=True)
    brand_id = fields.Many2one(string="Brand", related='product_id.brand_id')
    remarks = fields.Text(string="Remarks")
              # new fields added by WaqassAlii
    wh_id = fields.Many2one('stock.warehouse', string="Ware House")
    hs_code = fields.Char(string="HS code")
    tax_amount = fields.Float(string="Tax Amount",compute="_tax_amount_compute")
    # pro_available = fields.Float(related="product_id.qty_available", string="Product Available", store=True)
    pro_available = fields.Float(related='product_id.qty_available', store=True, string="Product Available")
    taxes_id = fields.Many2many('account.tax', string='Taxes %', domain=['|', ('active', '=', False), ('active', '=', True)])

    # @api.onchange('product_id')
    # def product_qty_location_check(self):
    #     if self.product_id:
    #         product = self.product_id
    #         pro_available = product.qty_available

    # def product_qty_location_check(self):
    #     for rec in self:
    #         if rec.product_id:
    #             rec.pro_available = rec.product_id.qty_available

    @api.onchange('price_unit', 'product_uom_qty', 'taxes_id')
    def _tax_amount_compute(self):
        for rec in self:
            tax_amount = 0
            if rec.price_unit:
                for tax in rec.taxes_id:
                    tax_amount += rec.price_unit * rec.product_uom_qty * tax.amount / 100
                rec.tax_amount = tax_amount

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


