# -*- coding: utf-8 -*-
from openerp import models, fields


class purchase_order(models.Model):
    _inherit = 'purchase.order'
    
    internal_number =  fields.Char(string='Référence interne',readonly=True, states={'draft':[('readonly',False)], 'sent':[('readonly',False)]},default='/')

    def wkf_confirm_order(self, cr, uid, ids, context=None):
        res = super(purchase_order,self).wkf_confirm_order(cr, uid, ids, context=context)
        for order in self.browse(cr, uid, ids, context=context):
            if order.internal_number == '/':
                self.write(cr, uid, [order.id], {'name':self.pool.get('ir.sequence').get(cr, uid, 'purchase.order.new_seq'),
                                                    'internal_number':order.name}, context=context)
        return res