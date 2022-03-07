# -*- encoding: utf-8 -*-
##############################################################################
#                                                                            #
#  OpenERP, Open Source Management Solution.                                 #
#                                                                            #
#  @author @author Daikhi Oualid <o_daikhi@esi.dz>                           #
#                                                                            #
#  This program is free software: you can redistribute it and/or modify      #
#  it under the terms of the GNU Affero General Public License as            #
#  published by the Free Software Foundation, either version 3 of the        #
#  License, or (at your option) any later version.                           #
#                                                                            #
#  This program is distributed in the hope that it will be useful,           #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of            #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              #
#  GNU Affero General Public License for more details.                       #
#                                                                            #
#  You should have received a copy of the GNU Affero General Public License  #
#  along with this program. If not, see <http://www.gnu.org/licenses/>.      #
#                                                                            #
##############################################################################

from odoo import models, fields, api, _


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    brand_id = fields.Many2one(comodel_name="product.brand", string="Brand")

    product_public_categ_id = fields.Many2one(
        comodel_name='product.public.category',
        string='Product Public Category',
        ondelete='cascade')

    applied_on = fields.Selection(selection_add=[
        ('22_product_brand', 'Product Brand'),
        ('21_product_public_categ', 'Product Public Category')],
        ondelete={'22_product_brand': 'cascade', '21_product_public_categ': 'cascade'})

    @api.onchange('applied_on')
    def _onchange_applied_on(self):
        """ clean fields based on applied on. """
        if self.applied_on != '0_product_variant':
            self.product_id = False
        if self.applied_on != '1_product':
            self.product_tmpl_id = False
        if self.applied_on != '2_product_category':
            self.categ_id = False
        if self.applied_on != '21_product_public_categ':
            self.product_public_categ_id = False
        if self.applied_on != '22_product_brand':
            self.brand_id = False

    @api.depends('applied_on', 'categ_id', 'product_tmpl_id', 'product_id', 'compute_price', 'fixed_price', \
                 'pricelist_id', 'percent_price', 'price_discount', 'price_surcharge', 'brand_id', 'product_public_categ_id')
    def _get_pricelist_item_name_price(self):
        """ handle name of item for new selection items. """
        super(ProductPricelistItem, self)._get_pricelist_item_name_price()
        for item in self.filtered(lambda i: i.applied_on in ('22_product_brand', '21_product_public_categ')):
            if item.product_public_categ_id and item.applied_on == '21_product_public_categ':
                item.name = _("Public Category: %s") % (item.product_public_categ_id.name)
            elif item.brand_id and item.applied_on == '22_product_brand':
                item.name = _("Brand: %s") % (item.brand_id.name)
