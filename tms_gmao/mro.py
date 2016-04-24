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

import time
from openerp.osv import fields, osv
#import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import netsvc

class mro_order(osv.osv):
    """
    Maintenance Orders
    """
    _name = 'mro.order'
    _inherit = 'mro.order'
    _description = 'Maintenance Order'

    MAINTENANCE_TYPE_SELECTION1 = [
        ('bm', 'Breakdown'),
        ('cm', 'Corrective'),
        ('pm', u'Programmée'),
    ]
        
    def _make_consume_parts_line(self, cr, uid, parts_line, context=None):
        stock_move = self.pool.get('stock.move')
        order = parts_line.maintenance_id
        # Internal shipment is created for Stockable and Consumer Products
        if parts_line.parts_id.type not in ('product', 'consu'):
            return False
        move_id = stock_move.create(cr, uid, {
            'name': order.name,
            'date': order.date_planned,
            'product_id': parts_line.parts_id.id,
            #'product_qty': parts_line.parts_qty,
            'product_uom_qty':parts_line.parts_qty,
            'product_uom': parts_line.parts_uom.id,
            'location_id': order.parts_location_id.id,
            'location_dest_id': (order.vehicle_id and order.vehicle_id.location_id.id) or (order.asset_id and order.asset_id.property_stock_asset.id) or False,
            'company_id': order.company_id.id,
        })
        order.write({'parts_move_lines': [(4, move_id)]}, context=context)
        return move_id

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms maintenance order.
        @return: Newly generated Parts Picking Id.
        """
        
        picking_id = False
        wf_service = netsvc.LocalService("workflow")
        picking_parts_id = False
        for order in self.browse(cr, uid, ids, context=context):
            for line in order.parts_lines: #make supply chain for each parts
                consume_parts_move_id = False
                #setting_val = self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_mro_order_supply_chain'], context)
                #print "setting_val", setting_val
                if self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_mro_order_supply_chain'], context)['tms_gmao_param_mro_order_supply_chain']:
                    picking_parts_id = self._create_picking_parts(cr, uid, order, context=context)
                    picking_parts_move_id = self._add_picking_parts_line(cr, uid, line, picking_parts_id, consume_parts_move_id, context=context)
                    consume_parts_move_id = self._make_consume_parts_line(cr, uid, line, context=context)
                    self._make_procurement_parts_line(cr, uid, line, picking_parts_move_id, context=context)
                    wf_service.trg_validate(uid, 'stock.picking', picking_parts_id, 'button_confirm', cr)
                    order.write({'state':'released'}, context=context)
                else:
                    consume_parts_move_id = self._make_consume_parts_line(cr, uid, line, context=context)
                    self.pool.get('stock.move').write(cr, uid, consume_parts_move_id, {'state': 'assigned'})
                    order.write({'state':'ready'}, context=context)
        return picking_parts_id

    def action_done(self, cr, uid, ids, context=None):
        #service_model, service_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'tms_bank_management', 'type_maintenance')
        amount = 0.0 
        if not self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_mro_order_supply_chain'], context)['tms_gmao_param_mro_order_supply_chain']:
            for mro in self.browse(cr, uid, ids, context):
                move_ids = [move.id for move in mro.parts_move_lines]
                self.pool.get('stock.move').write(cr, uid, move_ids, {'state': 'done'})
        self.write(cr, uid, ids, {'state': 'done', 'execution_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        mro_order_object = self.browse(cr,uid,ids[0],context=context)
        vehicle_cost = self.pool.get('fleet.vehicle.cost')
        for line in mro_order_object.parts_lines:
            amount +=line.price_unit * line.parts_qty
        amount += mro_order_object.other_cost
        cost_id = vehicle_cost.create(cr, uid, {
                    'vehicle_id': mro_order_object.vehicle_id.id,
                    'date': mro_order_object.date_execution,
                    'cost_subtype_id':mro_order_object.service_type_id.id,
                    'amount' : amount,
                     })

        return True

    def action_cancel(self, cr, uid, ids, context=None):
        for order in self.browse(cr, uid, ids, context=context):
            if order.state == 'released' and order.parts_picking_id and order.parts_picking_id.state not in ('draft', 'cancel'):
                raise osv.except_osv(
                    _('Cannot cancel maintenance order!'),
                    _('You must first cancel related internal picking attached to this maintenance order.'))
            self.pool.get('stock.move').action_cancel(cr, uid, [x.id for x in order.parts_move_lines])
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

#    def test_gmao_supply_chain_param(self, cr, uid, ids):
#        print "\n test_gmao_supply_chain_param method"
#        return self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_mro_order_supply_chain'], {})['tms_gmao_param_mro_order_supply_chain']

    _columns = {
        'vehicle_id': fields.many2one('fleet.vehicle', u'Véhicule', readonly=True, states={'draft': [('readonly', False)]}),
        'asset_id': fields.many2one('asset.asset', 'Asset'),
        'km_start': fields.float(u'Km de début', required=True),
        'maintenancier_id': fields.many2one('hr.employee', u'Maintenancier', help=u"Employé qui effectue la maintenance", readonly=True, states={'draft': [('readonly', False)]}),
        'user_id': fields.many2one('res.users', u'Responsable', readonly=True),
        'maintenance_type': fields.selection(MAINTENANCE_TYPE_SELECTION1, 'Maintenance Type', required=True, readonly=True, states={'draft': [('readonly', False)]}),
        'service_type_id': fields.many2one('fleet.service.type', u'Type d\'intervention', domain=[('mro_ok','=',True)], readonly=True, states={'draft': [('readonly', False)]}),
        'cost_id': fields.many2one('fleet.vehicle.cost', invisible=True, readonly=True),
        'alert_id': fields.many2one('tms.gmao.pm.alert', u'Alerte', invisible=True),
        'operation_ids': fields.one2many('mro.order.operation', 'mro_id', u'Opérations', readonly=True, states={'draft': [('readonly', False)]}),
        'parts_location_id':fields.many2one('stock.location', 'Source'),
        'other_cost' : fields.float('Autres charges'),
        }

    def _default_location_source(self, cr, uid, context=None):
        dummy,location_id  = self.pool['ir.model.data'].get_object_reference(cr,uid,"stock","stock_location_stock")
        if location_id:
            return location_id
        return False

    _defaults = {
        'km_start': 0.0,
        'user_id': lambda self, cr, uid, ctx: uid,
        'parts_location_id': _default_location_source,
        }

    def on_change_km_start(self, cr, uid, ids, km_start, context=None):
        assert km_start >= 0, 'Le kilomètre de départ ne doit pas être négatif !'
        return True

    def on_change_maintenance_type(self, cr, uid, ids, maintenance_type, context=None):
        result, domain = {'service_type_id': False}, {}
        if maintenance_type:
            service_type_ids = self.pool.get('fleet.service.type').search(cr, uid, [('maintenance_type','=',maintenance_type)])
            domain = {'service_type_id': [('id','in',service_type_ids)]}
            if len(service_type_ids)==1:
                result.update({'service_type_id': service_type_ids[0]})
        return {'value': result, 'domain': domain}

mro_order()


class mro_order_operation(osv.osv):
    _name="mro.order.operation"
    _description=u"Opérations de maintenance"

    _columns={
	'mro_id': fields.many2one('mro.order', u'mro id'),
        'employee_id': fields.many2one('hr.employee', u'Travailleur', required=True),
        'hours': fields.float(u'Nombre d\'heures', required=True),
        'description': fields.text('Description'),
        }

mro_order_operation()

class mro_request(osv.osv):
    """
    Maintenance Requests
    """
    _name = 'mro.request'
    _inherit = 'mro.request'
    _description = 'Maintenance Request'

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms maintenance request.
        @return: Newly generated Maintenance Order Id.
        """
        order = self.pool.get('mro.order')
        order_id = False
        for request in self.browse(cr, uid, ids, context=context):
            order_id = order.create(cr, uid, {
                'date_planned':request.requested_date,
                'date_scheduled':request.requested_date,
                'date_execution':request.requested_date,
                'origin': request.name,
                'state': 'draft',
                'maintenance_type': 'bm',
                'asset_id': request.asset_id and request.asset_id.id or False,
                'description': request.cause,
                'problem_description': request.description,
                'vehicle_id': request.vehicle_id and request.vehicle_id.id or False,
            })
        self.write(cr, uid, ids, {'state': 'run'})
        return order_id

    _columns = {
        'vehicle_id': fields.many2one('fleet.vehicle', u'Véhicule'),
        'asset_id': fields.many2one('asset.asset', 'Asset', required=False, readonly=True, states={'draft': [('readonly', False)]}),
        }

mro_request()

class mro_order_parts_line(osv.osv):
    _name = 'mro.order.parts.line'
    _inherit = 'mro.order.parts.line'
    _description = 'Maintenance Planned Parts'
    _columns = {
        'parts_id': fields.many2one('product.product', 'Parts', required=True, domain=[('spare_ok','=',True)]),
        'price_unit' : fields.float('Prix Unitaire'),
    }

mro_order_parts_line()
