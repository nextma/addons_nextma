from odoo import http

# class HrsftModePaiement(http.Controller):
#     @http.route('/hrsft_mode_paiement/hrsft_mode_paiement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/hrsft_mode_paiement/hrsft_mode_paiement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('hrsft_mode_paiement.listing', {
#             'root': '/hrsft_mode_paiement/hrsft_mode_paiement',
#             'objects': http.request.env['hrsft_mode_paiement.hrsft_mode_paiement'].search([]),
#         })

#     @http.route('/hrsft_mode_paiement/hrsft_mode_paiement/objects/<model("hrsft_mode_paiement.hrsft_mode_paiement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('hrsft_mode_paiement.object', {
#             'object': obj
#         })