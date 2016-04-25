# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 CodUP (<http://codup.com>).
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

from openerp import _
from openerp.osv import osv,fields


class mro_order(osv.osv):
    """
    Maintenance Orders
    """
    _inherit = 'mro.order'
    
    MAINTENANCE_TYPE_SELECTION = [
        ('bm', 'Breakdown'),
        ('cm', 'Corrective'),
        ('pm', u'Programmée'),
        ('tyre',u'Pneu'),
    ]


    def onchange_vehicle_id(self,cr,uid,ids,vehicle_id=False,ccontext=None):
        if not vehicle_id : 
            return {}
        vehicle=  self.pool.get('fleet.vehicle').browse(cr,uid,vehicle_id)
        value = vehicle.fuel_odometer
        return {'value':{'km_start':value}}

    _columns = {
        'other_cost' : fields.float('Autres frais'),
        'maintenance_type': fields.selection(MAINTENANCE_TYPE_SELECTION, 'Maintenance Type', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'tyre_lines' : fields.one2many('mro.order.parts.line.tyre','maintenance_id',string='Pneus',readonly=True, states={'draft':[('readonly',False)]}),
        'do_not_create_tyre' : fields.boolean('?'),
    }
    
    
    

    def test_if_parts(self, cr, uid, ids):
        """
        @return: True or False
        """
        res = super(mro_order,self).test_if_parts(cr,uid,ids)
        mro_order_object = self.browse(cr,uid,ids[0])
        if mro_order_object.maintenance_type=='tyre' and not mro_order_object.do_not_create_tyre:
            mro_order_object.do_not_create_tyre = True
            tms_tyre_serial = self.pool.get('tms.tyre.serial')
            for line in mro_order_object.tyre_lines:
                tyre_id = tms_tyre_serial.search(cr,uid,[('lot_id','=',line.ref.id)])
                vals = {
                  'vehicle_id':mro_order_object.vehicle_id.id,
                  'tyre_id':tyre_id[0] if tyre_id else [],
                  'position':line.position,
                  'start_date':mro_order_object.date_execution,
                  'start_odometer':mro_order_object.km_start,
                  'status':True,
                      }
                if tyre_id :
                    tyre = self.pool.get('tms.tyre.serial').browse(cr,uid,tyre_id[0])
                    if tyre.current_vehicle_id and tyre.current_vehicle_id.id<>mro_order_object.vehicle_id.id:
                        raise osv.except_osv(_('Error!'), _("Le pneu: %s est monté sur un autre véhicule.Veuillez le de-monter avant de le re-monter sur un autre.")%(line.ref.name,))
                    tyre.action_mount(vals)
                else :
                    print 'raise error'
        return res




class mro_order_parts_line_tyre(osv.osv):
    _name = 'mro.order.parts.line.tyre'
    
    _columns = {
        'product_id': fields.many2one('product.product', 'Produit',domain="[('tyre','=',True)]", required=True),
        'ref': fields.many2one('stock.production.lot', 'Référence',domain="[('product_id','=',product_id)]",required=True),
        'position' : fields.selection([('front_right','Avant droit'),('front_left','Avant gauche'),('back_right','Arrière droit'),('back_left','Arrière gauche')],'Position du pneu',required=True),
        'maintenance_id': fields.many2one('mro.order', 'Maintenance Order', select=True),
    }


    

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: