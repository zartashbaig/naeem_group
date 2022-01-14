# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################

from odoo import models,fields,api
from odoo.exceptions import ValidationError


class ProductBrand(models.Model):
    _inherit = 'product.template'

    brand_id = fields.Many2one('product.brand',string='Brand')


class BrandProduct(models.Model):
    _name = 'product.brand'


    name= fields.Char(String="Name")
    brand_image = fields.Binary()
    member_ids = fields.One2many('product.template', 'brand_id')
    product_count = fields.Char(String='Product Count', compute='get_count_products', store=True)

    @api.constrains('name')
    def check_name(self):
        brands = self.env['product.brand'].search([('name','=',self.name)])
        if brands.__len__()>1:
            raise ValidationError('You can not make brand with the same name')

    @api.depends('member_ids')
    def get_count_products(self):
        self.product_count = len(self.member_ids)


class BrandReportStock(models.Model):
    _inherit = 'stock.quant'

    brand_id  = fields.Many2one(related='product_id.brand_id',
        string='Brand', store=True, readonly=True)

#
# class ProductCategory(models.Model):
#     _name = 'product.category'
#
#
#     @api.constrains('name')
#     def check_name(self):
#         category = self.env['product.category'].search([('name','=',self.name)])
#         if category:
#             raise ValidationError('You can not make category with the same name')