# -*- coding: utf-8 -*-
# from odoo import http


# class CustomPurchaseSys(http.Controller):
#     @http.route('/custom_purchase_sys/custom_purchase_sys/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_purchase_sys/custom_purchase_sys/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_purchase_sys.listing', {
#             'root': '/custom_purchase_sys/custom_purchase_sys',
#             'objects': http.request.env['custom_purchase_sys.custom_purchase_sys'].search([]),
#         })

#     @http.route('/custom_purchase_sys/custom_purchase_sys/objects/<model("custom_purchase_sys.custom_purchase_sys"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_purchase_sys.object', {
#             'object': obj
#         })
