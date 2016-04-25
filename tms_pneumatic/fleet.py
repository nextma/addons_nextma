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
from openerp.tools.translate import _

class fleet_tyre_odometer(osv.Model):
    _name = 'fleet.tyre.odometer.history'
    _columns={
        'log_fuel_id' : fields.many2one('fleet.vehicle.log.fuel','log'),
        'tyre_id' : fields.many2one('tms.tyre.serial','Pneu'),
        'vehicle_id' : fields.many2one('fleet.vehicle','Vehicle'),
        'value' :fields.float('Valeur'),
        }

class fleet_vehicle_log_fuel(osv.Model):
    _inherit = 'fleet.vehicle.log.fuel'

    def action_done(self, cr, uid, ids, context):
        res = super(fleet_vehicle_log_fuel,self).action_done(cr, uid, ids, context)
        fleet_tyre = self.pool['tms.tyre.serial']
        tyre_odometer_obj = self.pool['fleet.tyre.odometer.history']
        for gasoil_order in self.browse(cr, uid, ids, context=context):
            tyre_ids = fleet_tyre.search(cr,uid,[('current_vehicle_id','=',gasoil_order.vehicle_id.id)])
            for tyre in fleet_tyre.browse(cr,uid,tyre_ids):
                tyre.write({'odometer_value':tyre.odometer_value+gasoil_order.km_driven,'calculate_odometer_value':tyre.calculate_odometer_value+gasoil_order.km_driven})
                tyre_odometer_obj.create(cr,uid,{'log_fuel_id':gasoil_order.id,'vehicle_id':gasoil_order.vehicle_id.id,'tyre_id':tyre.id,'value':gasoil_order.km_driven})
        return res

    def unlink(self, cr, uid, ids, context=None):
        fleet_tyre = self.pool['tms.tyre.serial']
        tyre_odometer_obj = self.pool['fleet.tyre.odometer.history']
        for gasoil_order in self.browse(cr, uid, ids, context=context):
            tyre_ids = fleet_tyre.search(cr,uid,[('current_vehicle_id','=',gasoil_order.vehicle_id.id)])
            for tyre in fleet_tyre.browse(cr,uid,tyre_ids):
                tyre.write({'odometer_value':tyre.odometer_value-gasoil_order.km_driven,'calculate_odometer_value':tyre.calculate_odometer_value-gasoil_order.km_driven})
                tyre_odometer_obj.create(cr,uid,{'log_fuel_id':gasoil_order.id,'vehicle_id':gasoil_order.vehicle_id.id,'tyre_id':tyre.id,'value':-gasoil_order.km_driven})
        return super(fleet_vehicle_log_fuel, self).unlink(cr, uid, ids, context)

class fleet_service(osv.osv):
    _inherit = 'fleet.vehicle'

    _columns = {
        'tyre_ids': fields.one2many('tms.tyre.serial','current_vehicle_id','Pneu monté'),
        }
