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
from odoo import fields, models


class ProductBrand(models.Model):
    _name = 'product.brand'
    _inherit = ['image.mixin']
    _description = 'Product Brands'
    _order = 'sequence'

    sequence = fields.Integer(help="Gives the sequence order when displaying "
                                   "a list of rules.")
    name = fields.Char(string='Name', required=True, translate=True)
    brand_image = fields.Binary(string='Brand Image')

    _sql_constraints = [('name_uniq', 'unique (name)', 'Brand name already exists !')]
