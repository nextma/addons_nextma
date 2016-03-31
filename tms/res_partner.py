# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields, osv

__author__ = "NEXTMA"
__version__ = "0.1"
#__date__ = u"22 Décembre 2013"

class res_partner(osv.Model):
    _name = 'res.partner'
    _inherit = 'res.partner' 
 
    def unlink(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'active' : False})
        return True

    def _get_param_customer_merchandise_select(self, cr, uid, ids, prop, unknow_none, context=None):
        param_value = self.pool.get('tms.config.settings').default_get(cr, uid, ['tms_param_customer_merchandise_select'], context)
        #print "\n param value: ", param_value
        res = {}
        for record in self.browse(cr, uid, ids, context):
            res[record.id] = param_value
        return res

    _columns = {
        'picking_merchandise_ids': fields.one2many('product.product', 'picking_customer_id', u'Marchandises transportées', help=u"Assignation des marchandises aux clients pour l'encodage des BLs."),
        'picking_merchandise_ok': fields.function(_get_param_customer_merchandise_select, method=True, type="boolean", string=u'Sélection des marchandises'),
        #'circuit_line_ids': fields.many2many('tms.grouping.circuit.line', 'tms_circuit_line_partner', 'partner_id', 'circuit_line_id', u'Circuits'),
        'pricelist_item_ids' : fields.many2many('product.pricelist.item', 'partner_item_rel', 'partner_id', 'item_id', u'Pricelist items'),
        'partner_invoiced_id' : fields.many2one('res.partner','Parténaire de facturation'),
        }

    _defaults = {
        'picking_merchandise_ok': lambda self, cr, uid, ctx: self.pool.get('tms.config.settings').default_get(cr, uid, ['tms_param_customer_merchandise_select'], ctx),
        }

res_partner()
