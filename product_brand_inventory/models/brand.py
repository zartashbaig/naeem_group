# -*- coding: utf-8 -*-
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
class ProductCategory(models.Model):
    _inherit = 'product.category'


    @api.constrains('name')
    def check_name(self):
        category = self.env['product.category'].search([('name','=',self.name)])
        if category.__len__()>1:
            raise ValidationError('You can not make category with the same name')