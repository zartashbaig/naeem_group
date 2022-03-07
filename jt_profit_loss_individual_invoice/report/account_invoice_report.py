# -*- coding: utf-8 -*-
##########################################################################
#                                                                               #
#    Part of Odoo. See LICENSE file for full copyright and licensing details.   #
#    Copyright (C) 2018 Jupical Technologies Pvt. Ltd. <http://www.jupical.com> #
#                                                                               #
##########################################################################

from odoo import api, fields, models, _


class AccountInvoiceReport(models.Model):

    _inherit = 'account.invoice.report'

    number = fields.Char('Invoice Number', readonly=True)
    cost_of_goods = fields.Float(string="COGS", readonly=True)
    net_pro_loss = fields.Float(string="Net Profit and Loss", readonly=True)

    def _select(self):
        return  super(AccountInvoiceReport, self)._select() + ", move.cost_of_goods as cost_of_goods," \
                                                              " move.net_pro_loss as net_pro_loss"

    def _sub_select(self):
        return  super(AccountInvoiceReport, self)._sub_select() + ", \
         move.cost_of_goods / (SELECT count(*) FROM account_move_line l where move_id = move.id) as cost_of_goods, " \
         "move.net_pro_loss / (SELECT count(*) FROM account_move_line l where move_id = move.id) as net_pro_loss" \


    def _group_by(self):
        return super(AccountInvoiceReport, self)._group_by() + ", move.name, move.cost_of_goods, move.net_pro_loss"


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
