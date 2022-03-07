# -*- coding: utf-8 -*-
##########################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
##########################################################################

from odoo import models, fields, api, _


class AccountInvoice(models.Model):

    _inherit = 'account.move'

    @api.depends('cost_of_goods')
    def set_profilt_lost_info(self):
        """
        This function updates the profit loss info based on COGS.
        :return: Net profit loss.
        """
        for invoice in self:
            invoice.net_pro_loss = invoice.amount_total - invoice.cost_of_goods
        return True

    @api.depends('state')
    def get_cogs_of_goods(self):
        """
        This function updates the COGS when validate invoice.
        :return: COGS of invoice.
        """
        for invoice in self:
            subtype = self.env['mail.message.subtype'].search([('res_model', '=', 'account.move'),
                                                               ('name', '=', 'Validated')], limit=1)
            mail_message = self.env['mail.message'].search([('model', '=', 'account.move'),
                                                            ('res_id', '=',
                                                             invoice.id),
                                                            ('subtype_id', '=', subtype.id)], limit=1)
            for invoice_line in invoice.invoice_line_ids:
                domain = [('product_id', '=', invoice_line.product_id.id),
                          ('origin', '=', invoice.invoice_origin)]
                print('domain', domain)
                if mail_message:
                    domain.append(('date', '<=', mail_message.create_date))
                elif invoice.state == 'posted':
                    current_date = fields.Date.today()
                    domain.append(('date', '<=', current_date))

                stock_moves = self.env['stock.move'].search(domain)
                inventory_value = 0
                quantity = 0
                price_unit_on_quant = 1.0
                for stock_move in stock_moves:
                    print('price_unit_on_quant', stock_move.price_unit)
                    price_unit_on_quant = stock_move.price_unit
                    if stock_move.product_id.cost_method == 'real':
                        self.inventory_value = stock_move.product_uom_qty * price_unit_on_quant

                    else:
                        amount_unit = stock_move.product_id.price_compute('standard_price', uom=stock_move.product_id.uom_id)[stock_move.product_id.id]
                        inventory_value = stock_move.product_uom_qty * amount_unit
                        # self.inventory_value = stock_move.product_uom_qty * stock_move.product_id
                        # .get_history_price(stock_move.company_id.id, 
                        #     date=self._context.get('date', fields.Datetime.now()))

                    if stock_move.location_id.usage == 'internal':
                        print('before_inventory_value',inventory_value)
                        inventory_value += inventory_value
                        print('afterinventory_value', inventory_value)
                        quantity += stock_move.product_uom_qty
                        print('quantity', quantity)
                if quantity != 0:
                    new_value = (invoice_line.quantity *
                                 inventory_value) / quantity
                    if abs(inventory_value) == new_value and abs(quantity) == invoice_line.quantity:
                        inventory_value = new_value
                        quantity = invoice_line.quantity
                    else:
                        inventory_value += new_value
                product_data = {
                    'product_id': invoice_line.product_id.id,
                    'inventory_value': inventory_value,
                    'quantity': quantity,
                    'invoice_quantity': invoice_line.quantity
                }
                print('product_data', product_data)
                if product_data.get('inventory_value') != 0 and product_data.get('quantity') != 0:
                    cogs = (product_data.get('inventory_value') / product_data.get('quantity')) * \
                        product_data.get('invoice_quantity')
                    print('cogs', cogs)
                    invoice.cost_of_goods += cogs

    cost_of_goods = fields.Float(
        string="COGS", compute='get_cogs_of_goods', store=True, copy=False)
    net_pro_loss = fields.Float(string="Net Profit and Loss",
                                compute='set_profilt_lost_info', store=True, copy=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
