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
import time
import datetime
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _

__author__ = "NEXTMA"
__version__ = "0.1"


class fleet_park(osv.osv):
    _name = 'fleet.park'

    def copy(self, cr, uid, id, default=None, context=None):
        if default is None:
            default = {}
        default = default.copy()
        if id:
            object_park=self.browse(cr,uid,id)
            if object_park:
                default.update({'name': '%s copy'%object_park.name, 'vehicle_ids': [], 'partner_ids': [], 'traject_ids': [], 'user_ids': [] })
        return super(fleet_park, self).copy(cr, uid, id, default, context=context)
    
    _columns = {
            'name' : fields.char(u'Nom du Parc', size=50, required=True, help=u"Définissez le nom du parc à segmenter(ex: Parc poids lourds)"),
            'note' : fields.text(u'Description'),
            'vehicle_ids' : fields.many2many('fleet.vehicle', 'vehicle_park_rel','park','vehicle', u'Véhicules', domain=[('vehicle_ok','=',True)], help=u"Définissez les véhicules contenu dans ce parc."),
            'partner_ids' : fields.many2many('res.partner', 'partner_park_rel','park','partner', u'Clients', help=u"Définissez les clients associés au parc, pour une rapidité d'encodage des voyages"),
            'traject_ids' : fields.many2many('product.product', 'traject_park_rel','park','traject', u'Trajets', domain=[('trajet_ok','=',True)], help=u"Définissez les trajets associés à ce parc."),
            'user_ids' : fields.one2many('res.users', 'park_id', u'Utilisateurs', readonly=True), #@TODO Is it really necessary ?
            'all_vehicle_ok' : fields.boolean(u'Tous les véhicules'),
            'all_traject_ok' : fields.boolean(u'Tous les trajets'),
            'all_partner_ok' : fields.boolean(u'Tous les clients'),
            }
    
    _defaults = {  
        'all_vehicle_ok': lambda *a: True,
        'all_traject_ok': lambda *a: True,
        'all_partner_ok': lambda *a: True,
        }
    
    _sql_constraints = [
        ('name_park_uniq', 'unique(name)', u'Le nom du parc doit être unique !')
    ]

fleet_park()

class fleet_vehicle_odometer(osv.Model):
    _name='fleet.vehicle.odometer'
    _inherit='fleet.vehicle.odometer'
    _description=u'Compteur'
    _order='date desc'

    _columns={
        'travel_ok': fields.boolean(u'voyage'),
        'fuel_ok': fields.boolean(u'gasoil'),
        }
    _defaults={
        'travel_ok': lambda *a: True,
        }

fleet_vehicle_odometer()

class fleet_vehicle(osv.osv):
    _name = 'fleet.vehicle'
    _inherit = 'fleet.vehicle'

    def return_action_to_open(self, cr, uid, ids, context=None):
        """ This opens the xml view specified in xml_id for the current vehicle """
        if context is None:
            context = {}
        if context.get('xml_id'):
            if context.get('tms'):
                res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'tms', context['xml_id'], context=context)
            else :
                res = self.pool.get('ir.actions.act_window').for_xml_id(cr, uid ,'fleet', context['xml_id'], context=context)
            res['context'] = context
            res['context'].update({'default_vehicle_id': ids[0]})
            if context.get('tms'):
                res['context'].update({'default_state':'info','default_type':'internal'})
            res['domain'] = [('vehicle_id','=', ids[0])]
            return res
        return False

    def get_data(self,cr,uid,context=None):
        vehicle_report_obj = self.pool.get('fleet.vehicle.report')
        ids = self.search(cr,uid,[(1,'=',1)])
        for vehicle in self.browse(cr,uid,ids,context=context):
            id = vehicle_report_obj.create(cr,uid,{'vehicle_id':vehicle.id})
            for bl in vehicle.bl_ids :
                vehicle_report_obj.browse(cr,uid,id).unlink()
                data = {
                        'vehicle_id':vehicle.id,
                        'product_id':bl.product_id.id,
                        'partner_id':bl.partner_id.id,
                        'date':bl.date,
                        }
                vehicle_report_obj.create(cr,uid,data)
                

    def create(self, cr, uid, data, context=None):
        truck_id = super(fleet_vehicle, self).create(cr, uid, data, context=context)
        truck = self.browse(cr, uid, truck_id, context=context)
        if truck:
            vehicle_ok = truck.vehicle_ok
            trailer_ok = truck.trailer_ok
#            truck_body = ""
#            if vehicle_ok:
#                truck_body = _('Le véhicule %s a été ajouté au parc !') % (truck.license_plate)
#            elif trailer_ok:
#                truck_body = _('La semi-remorque %s a été ajoutée au parc !') % (truck.license_plate)
            if context.get('generate_ok', True):
                self._generate_virtual_location(cr, uid, truck, vehicle_ok, trailer_ok, context)
                self._generate_analytic_account(cr, uid, truck, vehicle_ok, trailer_ok, context)
#            self.message_post(cr, uid, [truck_id], body=truck_body, context=context)
        return truck_id

    def write(self, cr, uid, ids, vals, context=None):
        for vehicle in self.browse(cr, uid, ids, context):
            changes = []
            if ('license_plate' in vals):
                data_stock={
                      'name' : 'Stock-%s-%s' %(vehicle.vehicle_ok and "veh" or "rem", vals['license_plate']),
                      }
                data_account={
                      'name' : 'Cpt-%s-%s' %(vehicle.vehicle_ok and "vehicle" or "remorque", vals['license_plate']),
                      }
                if vehicle.location_id:
                    self.pool.get('stock.location').write(cr, uid, vehicle.location_id.id, data_stock)
                if vehicle.account_id:
                    self.pool.get('account.analytic.account').write(cr, uid, vehicle.account_id.id, data_account)
            if 'hr_driver_id' in vals and vehicle.hr_driver_id.id != vals['hr_driver_id']:
                value = self.pool.get('hr.employee').browse(cr,uid,vals['hr_driver_id'],context=context).name
                olddriver = (vehicle.hr_driver_id.name) or _('None')
                changes.append(_(u"Chauffeur employé: de '%s' à '%s'") %(olddriver, value))
            if len(changes) > 0:
                self.message_post(cr, uid, [vehicle.id], body=", ".join(changes), context=context)
        return super(fleet_vehicle, self).write(cr, uid, ids, vals, context)

    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'log_fuel':[],
            'log_contracts':[],
            'log_services':[],
            'tag_ids':[],
            'vin_sn':'',
            'location_id': False,
            'account_id': False,
            #'counter_ids': [],
            #'vehicle_travel_ids': [],
            #'trailer_travel_ids': [],
            #'gasoil_order_external': [],
            #'gasoil_order': [],
            'trailer_modification_ids': [],
            'vehicle_modification_ids': [],
            #@DEPRECATED default['operational_ok'] = False, 
            'park_ids': [],
        })
        return super(fleet_vehicle, self).copy(cr, uid, id, default, context=context)

    def unlink(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'active' : False})
        return True

    def get_tms_vehicle_name(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        for record in self.browse(cr, uid, ids, context=context):
            res[record.id] = record.license_plate
        return res

    def onchange_vehicle_category_id(self, cr, uid, ids, category_id, context=None):
        data={}
        if category_id:
            category = self.pool.get('fleet.vehicle.category').browse(cr, uid, category_id)
            if category:
                data['hook_ok'] = category.hook_ok
        return {'value' : data}

    def onchange_vehicle_ok(self, cr, uid, ids, vehicle_ok, context=None):
        data={'park_ids': []}
        if not vehicle_ok:
            return data
        ids_search=self.pool.get('ir.model.data').search(cr,uid,[('name','=','tms_park_all')])
        if ids_search:
            object_data=self.pool.get('ir.model.data').browse(cr,uid,ids_search[0])
            if object_data:
                data.update({'park_ids': [object_data.res_id]})
        return {'value': data}

    def _generate_analytic_account(self, cr, uid, truck, vehicle_ok, trailer_ok, context):
        u'''Création de compte analytique pour le véhicule'''
        data = {'type' : 'normal', 'name' : "", 'state' : 'open'}
        result = False
        if vehicle_ok:
            data.update({'name' : 'Cpt-vehicle-%s' %truck.name})
            account_id = self.pool.get('account.analytic.account').create(cr, uid, data, context)
            if account_id:
                result = self.write(cr, uid, [truck.id], {'account_id': account_id}, context)
        elif trailer_ok:
            data.update({'name' : 'Cpt-remorque-%s' %(truck.name)})
            account_id = self.pool.get('account.analytic.account').create(cr, uid, data, context)
            if account_id:
                result = self.write(cr, uid, [truck.id], {'account_id': account_id}, context)
        return result
    
    def _generate_virtual_location(self, cr, uid, truck, vehicle_ok, trailer_ok, context): 
        u'''Création d'emplacement virtuel pour le véhicule'''
        data = {'chained_auto_packing': 'manual', 'chained_location_type': 'fixed', 'name': "", 'usage': 'internal'}
        result = False
        if vehicle_ok:
            data.update({'name': 'Stock-veh-%s' %(truck.name)})
            location_id = self.pool.get('stock.location').create(cr, uid, data, context)
            if location_id:
                result = self.write(cr, uid, [truck.id], {'location_id': location_id}, context)
        elif trailer_ok:
            data.update({'name': 'Stock-rem-%s' %(truck.name)})
            location_id = self.pool.get('stock.location').create(cr, uid, data, context)
            if location_id:
                result = self.write(cr, uid, [truck.id], {'location_id': location_id}, context)
        return result

#    def _get_tms_vehicle_name(self, cr, uid, ids, prop, unknow_none, context=None):
#        res = {}
#        for record in self.browse(cr, uid, ids, context=context):
#            if record.tms_vehicle_ok or record.tms_trailer_ok:
#                res[record.id] = record.license_plate
#            else:
#                res[record.id] = record.model_id.brand_id.name + '/' + record.model_id.modelname + ' / ' + record.license_plate
#        return res

    def _get_capacity(self, cr, uid, ids, field_names, arg, context=None):
        u"""calcul de la capacité du véhicule (volume) avec la semi-remorque associée"""
        data = {}
        if ids:
            reads = self.read(cr, uid, ids, ['gross_weight', 'volume'], context)
            for record in reads:
                    data[record['id']]= record['gross_weight'] - record['volume']
        return data

    def _get_current_vehicle_id(self, cr, uid, ids, name, args, context=None):    
        u"""Récupère le véhicule courant accroché à la semi-remorque"""
        data={}
        for truck in self.browse(cr, uid, ids, context=context):
            data[truck.id]=False
            if truck.vehicle_ok:
                continue
            modification_ids = self.pool.get('fleet.vehicle.modification').search(cr, uid, [('trailer_id','=',truck.id),('state','=','hooked')])
            if modification_ids:
                modification = self.pool.get('fleet.vehicle.modification').browse(cr, uid, modification_ids[0], context=context)
                data[truck.id] = modification.vehicle_id and modification.vehicle_id.id or False
        return data

    def _get_current_trailer_id(self, cr, uid, ids, name, args, context=None):
        u"""Récupération de la semi-remorque accrochée"""
        data={}
        for truck in self.browse(cr, uid, ids, context=context):
            data[truck.id]= False
            if truck.trailer_ok:
                continue
            modification_ids = self.pool.get('fleet.vehicle.modification').is_vehicle_hooked(cr, uid, truck.id, context)
            if modification_ids:
                for modification in self.pool.get('fleet.vehicle.modification').browse(cr, uid, modification_ids, context):
                    data[truck.id]= modification.trailer_id and modification.trailer_id.id or False        
        return data

    def _get_information_trailer(self, cr, uid, ids, name, args, context=None):
        u"""Récupération du poids sur la semi-remorque accrochée"""
        data={}
        for truck in self.browse(cr, uid, ids, context=context):
            data[truck.id]=0
            if truck.trailer_ok:
                continue
            modification_ids = self.pool.get('fleet.vehicle.modification').is_vehicle_hooked(cr, uid, truck.id, context)
            if modification_ids:
                for modification in self.pool.get('fleet.vehicle.modification').browse(cr, uid, modification_ids, context):
                    data[truck.id] = modification.trailer_id and modification.trailer_id.gross_weight or 0
        return data

    def _get_information_trailer_pv(self, cr, uid, ids, name, args, context=None):
        u"""Récupération du volume sur la semi-remorque accrochée"""
        data={}
        for truck in self.browse(cr,uid,ids, context=context):
            data[truck.id]=0
            if truck.trailer_ok:
                continue
            modification_ids = self.pool.get('fleet.vehicle.modification').is_vehicle_hooked(cr, uid, truck.id, context)
            if modification_ids:
                for modification in self.pool.get('fleet.vehicle.modification').browse(cr, uid, modification_ids, context):
                    data[truck.id] = modification.trailer_id and modification.trailer_id.volume or 0
        return data

    def _get_capacity_global(self, cr, uid, ids, prop, unknow_none, context):
        u"""Calcul de la capacité"""
        data={}
        if ids:
            for record in self.browse(cr, uid, ids, context):
                data[record.id] = 0
                if record.trailer_ok:
                    continue
                if record.trailer_id:
                    data[record.id] = record.ptc_trailer - record.pv_trailer + record.volume
        return data

    def _get_disponibility(self, cr, uid, ids, name, args, context=None): 
        u"""Disponibilité du véhicule sur la base des voyages en cours"""
        data={}
        my_date = time.strftime('%Y-%m-%d %H:%M:%S')
        my_date_start = time.strftime('%Y-%m-%d 00:00:00')
        my_date_end = time.strftime('%Y-%m-%d 23:59:59')
        for vehicle in self.browse(cr, uid, ids, context=context):
            data[vehicle.id] = {
                                'disponibility': 'available',
                                'current_travel': u'Pas de voyage',
                                'current_date_travel': False,
                               }
            #if self.pool.get('tms.param').get_value_by_reference(cr,uid,'tms','tms_param_include_tax') == True: @TODO try to understand it !
            cr.execute(
                       """
                       select id, name, date from tms_picking 
                       where date >= '%s' and date<= '%s'
                        and vehicle_id = %d
                        and state != 'cancel'
                        order by
                        date desc
                       """%(my_date_start, my_date_end, vehicle.id)
                       )

            for item in cr.dictfetchall():
                data[vehicle.id]['current_travel'] = u'%s' %(item['name'])
                data[vehicle.id]['current_date_travel'] = item['date']
                data[vehicle.id]['disponibility'] = 'unavailable'
                break
        return data
    def get_travel_disponibility(self, cr, uid, picking_id, vehicle_id, date, date_end): 
        u"""Disponibilité du véhicule pour le voyage"""
        cr.execute(
                       """
                       SELECT id, name AS name FROM tms_picking 
                       WHERE id != %s
                       AND ((date >= '%s' and date<= '%s') OR (date_end >= '%s' and date_end <= '%s'))
                       AND vehicle_id = %d
                       AND state NOT IN ('draft', 'cancel')
                       ORDER BY
                       DATE desc
                       """%(picking_id, date, date_end, date, date_end, vehicle_id)
                       )

        for item in cr.dictfetchall():
            return [False, item['name']]
        return [True]

    def _get_odometer(self, cr, uid, ids, odometer_id, arg, context):
        res = dict.fromkeys(ids, 0)
        for record in self.browse(cr,uid,ids,context=context):
            ids = self.pool.get('fleet.vehicle.odometer').search(cr, uid, [('vehicle_id', '=', record.id),('travel_ok','=',True)], limit=1, order='value desc')
            if len(ids) > 0:
                res[record.id] = self.pool.get('fleet.vehicle.odometer').browse(cr, uid, ids[0], context=context).value
        return res

    def _set_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if value:
            date = fields.date.context_today(self, cr, uid, context=context)
            data = {'value': value, 'date': date, 'vehicle_id': id}
            return self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)

    def _get_fuel_odometer(self, cr, uid, ids, odometer_id, arg, context):
        res = dict.fromkeys(ids, 0)
        for record in self.browse(cr, uid, ids, context=context):
            ids = self.pool.get('fleet.vehicle.log.fuel').search(cr, uid, [('vehicle_id', '=', record.id)], limit=1, order='counter_new desc')
            if len(ids) > 0:
                res[record.id] = self.pool.get('fleet.vehicle.log.fuel').browse(cr, uid, ids[0], context=context).counter_new
        return res

    def _set_fuel_odometer(self, cr, uid, id, name, value, args=None, context=None):
        if value:
            date = fields.date.context_today(self, cr, uid, context=context)
            data = {'value': value, 'date': date, 'vehicle_id': id, 'travel_ok': False, 'fuel_ok': True}
            return self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)

    def _get_stock_move_ids(self, cr, uid, ids, name, args, context=None):
        u"""inventaire de l'emplacement virtuel du véhicule"""
        data={}
        for record in self.browse(cr, uid, ids, context=context):
            if record.location_id:
                location_id = record.location_id.id
                data[record.id] = self.pool.get('stock.move').search(cr, uid, ['|',('location_id','=',location_id),('location_dest_id','=',location_id), ('state','=','done')])
        return data
    def _get_if_in_users_parks(self,cr, uid, ids, name, args,context):
        if not ids: return {}
        current_user = self.pool.get('res.users').browse(cr,uid,context.get('uid'))
        res = {}
        for line in self.browse(cr, uid, ids, context=context):
            res[line.id] = False
            for park in line.park_ids:
                if current_user.park_id.id ==  park.id:
                    res[line.id] = True
                    return res
        return res    
    _columns = {
        'name': fields.function(get_tms_vehicle_name, type="char", string='Nom', store=True),
        'active': fields.boolean(u'Activé'),
        'default_code': fields.char(u'Référence interne', size=64, select=True),
        'date_start_circulation': fields.date(u'Date mise en circulation'),
        'total_axle': fields.integer(u'Nombre d\'essieux'),
        'length': fields.float(u'Longueur', digits=(10,3)),
        'width': fields.float(u'Largeur', digits=(10,3)),
        'height': fields.float(u'Hauteur', digits=(10,3)),
        'tyre_qty': fields.float(u'Nombre de pneus', digits=(10,3)),
        'gross_weight': fields.float(u'P.T.C', digits=(10,3)),
        'volume': fields.float(u'Volume', help="Volume en m3."),
        'capacity': fields.function(_get_capacity, method=True, type="float", string="Capacité", help=u"P.T.C - Volume"),
        'stock_move_ids': fields.function(_get_stock_move_ids, type='one2many', string=u'Flux de stock', obj="stock.move", method=True),
        'account_line_ids': fields.related('account_id', 'line_ids', type='one2many', relation='account.analytic.line', string=u'Flux analytiques', readonly=True),
        'model_id': fields.many2one('fleet.vehicle.model', u'Modèle', required=False, help=u'Modèle du véhicule'),
        'partner_id': fields.many2one('res.partner', u'Vendeur'),
        #'owner_id' : fields.many2one('res.partner', u'Propriétaire'), #@EXPLAIN to play the role of the actual driver_id field -> res_partner
        'merchandise_id': fields.many2one('tms.travel.palet.merchandise', u'Type de transport'), 
        'location_id': fields.many2one('stock.location', u'Emplacement'),
        'account_id': fields.many2one('account.analytic.account', u'Compte analytique'),
        'category_id': fields.many2one('fleet.vehicle.category', u'Catégorie', required=False),
        'brand_id': fields.many2one('fleet.vehicle.model.brand', u'Marque'),
        ######### Trailer only related fields
        'trailer_ok': fields.boolean(u'Semi-Remorque'),
        'vehicle_code' : fields.char(u'Référence', size=50),
        #'counter_current' : fields.function(_get_counter_current, type="float", string=u"Kilométrage sur base des voyages"),
        'vehicle_id': fields.function(_get_current_vehicle_id, u'Véhicule accroché', type='many2one', method=True, relation='fleet.vehicle'),
        'trailer_modification_ids' : fields.one2many('fleet.vehicle.modification', 'trailer_id', u'Historique modifications', readonly=True, ondelete="cascade"),
        #'trailer_travel_ids' : fields.one2many('tms.travel', 'trailer_id', string=u'Voyages', readonly=True, ondelete="set null"),
        'odometer': fields.function(_get_odometer, fnct_inv=_set_odometer, type='float', string=u'Compteur voyage', help=u'Compteur voyage'),
        'fuel_odometer': fields.function(_get_fuel_odometer, fnct_inv=_set_fuel_odometer, type='float', string=u'Compteur gasoil', help=u'Compteur gasoil au moment de cet encodage.'),
        ######### Vehicle only related fields
        #@DEPRECATED 'operational_ok' : fields.boolean(_(u"Véhicule fonctionnel")),
        'vehicle_ok': fields.boolean(u'Véhicule'),
        'cylinder_qty': fields.integer(u'Nombre Cylindres'),
        'counter_basic': fields.float(u'Compteur de base', digits=(20,3)),
        'consumption_gasoil': fields.float(u'Consommation carburant %', digits=(50,3)),
        'hook_ok': fields.related('category_id', 'hook_ok', type='boolean', string=u'Peut être accroché'),
        'trailer_id': fields.function(_get_current_trailer_id, type='many2one', relation="fleet.vehicle", string=u'Semi-remorque', method=True),
        'pv_trailer': fields.function(_get_information_trailer_pv, string=u'PV Remorque', method=True, type = 'float', digits=(16,3)),
        'ptc_trailer': fields.function(_get_information_trailer, string=u'PTC Remorque', method=True, type = 'float', digits=(16,3)),
        'capacity_global': fields.function(_get_capacity_global, method=True, type="float", string=u"Capacité globale", digits=(16,3), help=u"P.T.C - ( PV_SemiR + PV_Tracteur )"),
        #'counter_old': fields.function(_get_counter,type='float',string=_(u'Ancien Compteur'),method=True, digits=(16,3),multi='sums'),
        #'counter_current_gasoil': fields.function(_get_counter,type='float',string=_(u'Compteur sur base carburant'),method=True, digits=(16,3),multi='sums',help=_(u'compteur courant basé sur les bons saisis')),
        #'counter_current': fields.function(_get_counter_current_travel,type='float',string=_(u'Compteur sur base voyage'),method=True, digits=(16,3),help=_(u'Compteur courant basé sur les voyages effectués')),
        #'counter_current_estimated': fields.function(_get_counter,type='float',string=_(u'Compteur courant estimé'),method=True, digits=(16,3),multi='sums'),
        'disponibility': fields.function(_get_disponibility, method=True, type='selection', string=u'statut-voyage', multi='current_travel', 
                        selection=[('available', u'Disponible'),('unavailable', u'En voyage')]),
        'current_travel': fields.function(_get_disponibility, method=True, type='char', string=u'Voyage en cours', multi='current_travel'),
        'current_date_travel' : fields.function(_get_disponibility,method=True,type='datetime',string=u'date voyage',multi='current_travel'),
        'hr_driver_id': fields.many2one('hr.employee', u'Chauffeur employé', domain=[('driver_ok','=',True)]),
        #'gasoil_order': fields.one2many('tms.gasoil.order','vehicle',string=_('Bons gasoil'),readonly=True,ondelete="set null"),
        #'gasoil_order_external': fields.one2many('tms.gasoil.order.external','vehicle',string=_(u'Bons gasoil externes'),readonly=True ),
        #'counter_ids': fields.one2many('tms.truck.counter', 'vehicle_id', u'compteurs carburant', readonly=True, ondelete="cascade"),
        #'vehicle_travel_ids': fields.one2many('tms.travel', 'vehicle_id', string=u'Voyages', readonly=True, ondelete="set null"),  
        'vehicle_modification_ids': fields.one2many('fleet.vehicle.modification', 'vehicle_id', u'Affectation remorques', readony=True),
        'park_ids': fields.many2many('fleet.park', 'vehicle_park_rel', 'vehicle', 'park', u'Parc Véhicule'),
        'owner': fields.char(u'Propriétaire', size=32),
        'manager': fields.char(u'Exploitant', size=32),
        'vehicle_in_park':fields.function(_get_if_in_users_parks, method=True, type='boolean',string='in users park',store=True ),
        
        'bl_ids': fields.one2many('tms.picking', 'vehicle_id', u'Bls associées', readony=True),
        'partner_id' : fields.related('bl_ids','partner_id', type='many2one', relation='res.partner', string="Clients",store=True),
        'product_id' : fields.related('bl_ids','product_id', type='many2one', relation='product.product', string="Trajets",store=True),
        'date' : fields.related('bl_ids','date', type='date', string="Date",store=True),
        'imprimer_rapport' : fields.boolean("Imprimer dans le rapport d'activité"),
        'required_vin' :  fields.boolean('Numéro de chassis obligatoire'),
        }

    _defaults = {
        'vehicle_ok': lambda *a: True,
        'imprimer_rapport' :lambda *a: True,
        'volume' : lambda *a : 0.0,
        'total_axle' : lambda *a : 1,
        'length' : lambda *a: 0,
        'gross_weight':lambda *a: 20.0,
        'active': lambda *a: True,
        'disponibility': lambda *a : 'available',
        'required_vin': lambda self, cr, uid, ctx: self.pool.get('tms.config.settings')._get_tms_setting_default_values(cr, uid,['required_vin'], ctx),
    }

    _sql_constraints = [
        ('date_vehicle_check', "CHECK ( acquisition_date <= date_start_circulation )", "La date de mise en circulation doit être supérieure à celle d'acquisition"),
    ]

fleet_vehicle()

class fleet_vehicle_category(osv.osv):
    u"""Catégorie de véhicule"""
    _name = 'fleet.vehicle.category'
    #_description = u"Catégorie de véhicule"
    _columns = {
            'vehicle_ok': fields.boolean(u'Catégorie véhicule TMS'),
            'trailer_ok': fields.boolean(u'Catégorie semi-remorque TMS'),
            'name': fields.char(u'Nom', size=64),
            'hook_ok': fields.boolean(u'Peut être accroché'),
            'vehicle_ids': fields.one2many('fleet.vehicle', 'category_id', string=u'véhicules', domain=[('vehicle_ok','=',True)], ondelete="set null"),
            'trailer_ids': fields.one2many('fleet.vehicle', 'category_id', string=u'semi-remorques', domain=[('trailer_ok','=',True)], ondelete="set null"),
            'note' : fields.text(u'Description'),
        }
    _default = {
            #'hook_ok' : True,
            'vehicle_ok': True,
                }
    _sql_constraints = [
        ('fleet_vehicle_category_name_uniq', 'unique(name)', u'Le nom de catégorie doit être unique !')
    ]
    
fleet_vehicle_category()

class fleet_vehicle_model(osv.Model):
    _name = 'fleet.vehicle.model'
    _inherit = 'fleet.vehicle.model'
    #_description = 'Modèles de véhicule'

    _columns = {
        #'vehicle_ok': fields.boolean(u'Modèle véhicule TMS'),
        'vehicle_ids' : fields.one2many('fleet.vehicle', 'model_id', u'Véhicules', ondelete="set null"),
        'note' : fields.text(u'Description'),
    }

    _sql_constraints = [
        ('fleet_vehicle_model_name_uniq', 'unique(name)', u'Le nom de modèle doit être unique !')
    ]
fleet_vehicle_model()

class fleet_vehicle_model_brand(osv.Model):
    _name = 'fleet.vehicle.model.brand'
    _inherit = 'fleet.vehicle.model.brand'
    #_description = u'Marque de véhicule'

    _columns = {
        'vehicle_ok': fields.boolean(u'Marque véhicule TMS'),
        'trailer_ok': fields.boolean(u'Marque semi-remorque TMS'),
        'name': fields.char(u'Marque', size=64, required=True),
        'model_ids' : fields.one2many('fleet.vehicle.model', 'brand_id', u'Modèles', ondelete="set null"),
        'vehicle_ids': fields.one2many('fleet.vehicle', 'brand_id', u'Véhicules', ondelete="set null", domain=[('vehicle_ok','=',True)], help=u"Véhicules de cette marque"),
        'trailer_ids': fields.one2many('fleet.vehicle', 'brand_id', u'Semi-Remorques', ondelete="set null", domain=[('trailer_ok','=',True)], help=u"Semi-remorques de cette marque"),
        'note': fields.text(u'Description'),
    }
    _defaults = {
        'vehicle_ok': True,
                }

    _sql_constraints = [
        ('fleet_model_brand_name_uniq', 'unique(name)', u'Le nom de modèle doit être unique !')
    ]
fleet_vehicle_model_brand()

class fleet_vehicle_modification(osv.osv):
    u"""Modification du parc (accrochage/décrochage véhicule - semi-remorque)"""
    _name = 'fleet.vehicle.modification'
    _description = u'Modification camion'

    def create(self, cr, uid, vals, context=None):
        if ('name' not in vals) or (vals.get('name') == '/'):
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'fleet.vehicle.modification')
        return super(fleet_vehicle_modification, self).create(cr, uid, vals, context)
    
    def copy(self, cr, uid, id, default=None, context={}):
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'fleet.vehicle.modification')
        default['state'] = 'progress'
        return super(fleet_vehicle_modification, self).copy(cr, uid, id, default, context)
    
    def unlink(self, cr, uid, ids, context=None):
        if ids:
            for modification in self.browse(cr,uid,ids):
                if modification.state != 'progress':
                    raise osv.except_osv(u'Suppression impossible !', u'Vous ne pouvez pas supprimer une modification déjà traitée.')
        return super(fleet_vehicle_modification, self).unlink(cr, uid, ids, context)   

    def set_unhook(self, cr, uid, ids, context={}):
        u"""Décrocher semi-remorque"""
        for modification in self.browse(cr,uid,ids,context):
            if modification.state == 'hooked' :
                date_unhook=False
                if modification.date_unhook:
                    date_unhook = modification.date_unhook
                else:
                    date_unhook = time.strftime('%Y-%m-%d %H:%M:%S')
                res_modification = self.write(cr, uid, modification.id, {'state':'unhooked','date_unhook': date_unhook}, context=context)
                if res_modification:
                    data_obj = self.pool.get('ir.model.data')
                    res = data_obj.get_object_reference(cr, uid, 'tms', 'fleet_vehicle_modification_form')
                    context.update({'view_id': res and res[1] or False})
                    message =u"La semi-remoque %s a été décrochée du véhicule %s." %(modification.trailer_id.name, modification.vehicle_id.name)
                    self.pool.get('fleet.vehicle.modification').log(cr, uid, modification.id, message, context=context)
        return True

    def is_trailer_hooked(self,cr, uid, trailer_id, context={}):
        u"""Teste si la semi-remorque est accrochée"""
        modification_ids = self.search(cr, uid, [('trailer_id', '=', trailer_id), ('state', '=', 'hooked')])
        if len(modification_ids) > 0:
            return modification_ids
        return False

    def is_vehicle_hooked(self,cr, uid, vehicle_id, context={}):
        u"""Teste si le véhicule est accroché"""
        modification_ids = self.search(cr, uid, [('vehicle_id', '=', vehicle_id), ('state', '=', 'hooked')])
        if len(modification_ids) > 0:
            return modification_ids
        return False

    def set_hook(self, cr, uid, ids, context={}):
        u"""Accrocher semi-remorque"""
        for modification in self.browse(cr, uid, ids, context={}):
            if self.is_vehicle_hooked(cr, uid, modification.vehicle_id.id, context) :
                raise osv.except_osv(u'Erreur', u'Le vehicule est déjà accroché à une semi-remorque')
            else:
                if self.is_trailer_hooked(cr, uid, modification.trailer_id.id, context):
                    raise osv.except_osv(u'Erreur', u'La semi-remorque est déjà accroché à un vehicule')
                else:
                    date_hook = False
                    if modification.date_hook:
                        date_hook = modification.date_hook
                    else:
                        date_hook = time.strftime('%Y-%m-%d %H:%M:%S')
                    res_modification = self.write(cr, uid, modification.id, {'state':'hooked','date_hook': date_hook}, context=context)
                    if res_modification:
                        data_obj = self.pool.get('ir.model.data')
                        res = data_obj.get_object_reference(cr, uid, 'tms', 'fleet_vehicle_modification_form')
                        context.update({'view_id': res and res[1] or False})
                        message =u"La semi-remoque %s a été accrochée au véhicule %s." %(modification.trailer_id.name, modification.vehicle_id.name)
                        self.pool.get('fleet.vehicle.modification').log(cr, uid, modification.id, message, context=context)
        return True

    def onchange_vehicle_code(self, cr, uid, ids, code, context={}):
        u"""Evènement lors du changement du code véhicule"""
        data={}
        if code:
            vehicle_ids = self.pool.get('fleet.vehicle').search(cr, uid, [('default_code','=',code),('vehicle_ok','=',True)])
            if vehicle_ids:
                vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_ids[0])
                if vehicle:
                    data['vehicle'] = vehicle.id
            else:
                data['vehicle'] = False
        return {'value' : data}
    
    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id, context={}):
        u"""évènement lors du changement du véhicule"""
        data={}
        if vehicle_id:
            vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id)
            if vehicle:
                data['vehicle_code'] = vehicle.default_code
        return {'value' : data}

    _columns = {
        'name': fields.char(u'Ref modification', size=20, required=True, readonly=True),
        'vehicle_id': fields.many2one('fleet.vehicle', u'vehicle', states={'progress': [('readonly', False)]}, domain=[('hook_ok','=',True),('vehicle_ok','=',True)]),
        'vehicle_code' : fields.char(u'Référence', size=50), 
        'date_hook': fields.datetime(u'Accroché le', help=u"Date d'accrochage"),
        'date_unhook': fields.datetime(u'Décroché le', help=u"Date de décrochage"),
        'trailer_id': fields.many2one('fleet.vehicle', u'Semi-Remorque', states={'progress': [('readonly', False)]}, domain=[('trailer_ok','=',True)]),
        'state': fields.selection([('unhooked', u'Décroché'),('hooked', u'Accroché'),('progress', u'En cours')], u'Statut', readonly=True, select=True),
        }
    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'state': lambda *a: 'progress',
        }
        
    _sql_constraints = [
        ('fleet_vehicle_modification_name_uniq', 'unique(name)', u'Le nom d\'une modification doit être unique')
    ]
fleet_vehicle_modification()

class fleet_vehicle_log_contract(osv.Model):
    _name = 'fleet.vehicle.log.contract'
    _inherit = 'fleet.vehicle.log.contract'

    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {'value': {'account_id': False}}
        datas = self.pool.get('fleet.vehicle').read(cr, uid, vehicle_id, ['account_id'])
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        odometer_unit = vehicle.odometer_unit
        driver = vehicle.driver_id.id
        return {
            'value': {
                'account_id': datas['account_id'] and datas['account_id'][0] or False,
                'odometer_unit': odometer_unit,
                'purchaser_id': driver,
            }
        }

    _columns = {
        'vehicle_ok': fields.boolean(u'Véhicule TMS'),
        'trailer_ok': fields.boolean(u'Semi-remorque TMS'),
        'account_id': fields.many2one('account.analytic.account', u'Compte analytique'),
    }
    _defaults = {
        'vehicle_ok': True,
                }
    _sql_constraints = [
        ('date_check', "CHECK ( start_date <= expiration_date )", "La date d'expiration doit être supérieure à celle de début"),
    ]

fleet_vehicle_log_contract()

class fleet_vehicle_cost(osv.Model):
    _name = 'fleet.vehicle.cost'
    _inherit = 'fleet.vehicle.cost'

    def _get_fuel_odometer(self, cr, uid, ids, odometer_id, arg, context):
        res = dict.fromkeys(ids, False)
        for record in self.browse(cr, uid, ids, context=context):
            if record.fuel_odometer_id:
                res[record.id] = record.fuel_odometer_id.value
        return res

    def _set_fuel_odometer(self, cr, uid, id, name, value, args=None, context=None):
        cost = self.browse(cr, uid, id, context=context)
        # to avoid the creation of a null value fuel odometer for a an external gasoil order
        model, model_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'tms', 'type_service_refueling_external')
        if model_id and (cost.cost_subtype_id.id == model_id):
            return True
        if not value:
            raise osv.except_osv(_(u'Operation not allowed!'), _(u'Emptying the odometer value of a vehicle is not allowed.'))
        date = self.browse(cr, uid, id, context=context).date
        if not(date):
            date = fields.date.context_today(self, cr, uid, context=context)
        vehicle_id = cost.vehicle_id
        data = {'value': value, 'date': date, 'vehicle_id': vehicle_id.id, 'fuel_ok': True, 'travel_ok': False}
        fuel_odometer_id = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data, context=context)
        return self.write(cr, uid, id, {'fuel_odometer_id': fuel_odometer_id}, context=context)

    _columns = {
        'vehicle_ok': fields.boolean(u'Véhicule TMS'),
        'trailer_ok': fields.boolean(u'Semi-remorque TMS'),
        'fuel_odometer_id': fields.many2one('fleet.vehicle.odometer', u'Compteur gasoil', help='Référence du dernier compteur gasoil au moment de cet encodage.'),
        'fuel_odometer': fields.function(_get_fuel_odometer, fnct_inv=_set_fuel_odometer, type='float', string=u'Compteur gasoil', help=u'Compteur gasoil au moment de cet encodage.'),
    }
    _defaults = {
        'vehicle_ok': True,
                }

fleet_vehicle_cost()

class fleet_vehicle_log_fuel(osv.Model):
    _name = 'fleet.vehicle.log.fuel'
    _inherit = 'fleet.vehicle.log.fuel'
    _order = 'date_order desc'

    def create(self, cr, uid, vals, context=None):
        u"""Méthode créer"""
        #if 'vehicle_id' in vals:
        #    self.check_fuel_limit(cr, uid, vals['vehicle_id'], vals['amount'], vals['liter'], context)
        if ('name' not in vals) or (vals.get('name')=='/'):
            order_type = vals.get('type', "")
            if order_type:
                seq_type_name = 'fleet.vehicle.log.fuel.%s'%order_type
                vals['name'] = self.pool.get('ir.sequence').get(cr, uid, seq_type_name)
            if order_type == 'internal':
                vals['state']='draft'
        return super(fleet_vehicle_log_fuel, self).create(cr, uid, vals, context) 
    
    def unlink(self, cr, uid, ids, context=None):
        u"""méthode de suppression"""
        if ids:
            for fuel_log in self.browse(cr, uid, ids, context=context):
                if fuel_log.state == 'done':
                    raise osv.except_osv(u'Suppression impossible !', u'Vous ne pouvez pas supprimer un bon carburant interne déjà validé.')
                if fuel_log.fuel_odometer_id:
                    self.pool.get('fleet.vehicle.odometer').unlink(cr, uid, fuel_log.fuel_odometer_id.id)
                self.pool.get('fleet.vehicle.cost').unlink(cr, uid, fuel_log.cost_id.id)
        return super(fleet_vehicle_log_fuel, self).unlink(cr, uid, ids, context)

    def write(self, cr, uid, ids, vals, context=None):
        for fuel_log in self.browse(cr, uid, ids, context):
            if fuel_log.type == 'internal' and vals.get('fuel_odometer', False):
                self.pool.get('fleet.vehicle.odometer').write(cr, uid, fuel_log.fuel_odometer_id.id, {'value': vals['fuel_odometer']})
        return super(fleet_vehicle_log_fuel,self).write(cr, uid, ids, vals, context)

    def action_done(self, cr, uid, ids, context):
        u"""Action de traitement du bon carburant"""
        data_obj = self.pool.get('ir.model.data')
        for gasoil_order in self.browse(cr, uid, ids, context=context):
            if gasoil_order.counter_old > gasoil_order.counter_new:
                raise osv.except_osv(u'Alerte !', u'Le nouveau compteur est inferieur à l\'ancien !')
            #@TODO edit this part after TMS parameters are defined
            #elif self.pool.get('tms.param').get_value_by_reference(cr,uid,'tms','tms_param_only_travel') == False:
            #    if len(object_bon_gasoil.assigned_travels_id) == 0:
            #        raise osv.except_osv(_(u'Voyages obligatoires'), _(u'Vous devez sélectionner obligatoirement au moins un voyage pour valider le bon carburant interne, ou changer le paramètre pour avoir la possibilité de ne pas sélectionner de voyages.'))
            else:
                if gasoil_order.vehicle_id and gasoil_order.location_id:
                    move_id = self.pool.get('stock.move').create(cr, uid, {
                                'name': gasoil_order.name,
                                'product_id': gasoil_order.gasoil_id and gasoil_order.gasoil_id.id or False,
                                'product_uom_qty': gasoil_order.liter,
                                'product_uom': gasoil_order.gasoil_id.product_tmpl_id and gasoil_order.gasoil_id.product_tmpl_id.uom_id and gasoil_order.gasoil_id.product_tmpl_id.uom_id.id or False,
                                'location_id': gasoil_order.cistern_id and gasoil_order.cistern_id.id or False,
                                'location_dest_id': gasoil_order.location_id and gasoil_order.location_id.id or False,
                                'date': gasoil_order.date,
                                'state': 'done',
                                'note': u'Carburant',
                    })
                for gasoil_external in gasoil_order.assigned_external_ids:
                    self.pool.get('fleet.vehicle.log.fuel').write(cr, uid, [gasoil_external.id], {'state': 'assigned'})
                #@TODO check how to validate tms_travel object also
                #for read in self.read(cr,uid,ids,['assigned_travels_id','assigned_partial_travels_id']):
                #    self.pool.get('tms.travel').hold(cr,uid,read['assigned_travels_id'],None)
                #    self.pool.get('tms.gasoil.order.partial').hold(cr,uid,read['assigned_partial_travels_id'],None)
                self.write(cr, uid, [gasoil_order.id], {'state': 'done'})
                #self.message_post(cr, uid, [gasoil_order.id], body=u"Le bon de carburant interne %s a été validé." %(gasoil_order.name), context=context)
        return True

    def action_cancel(self, cr, uid, ids, context=None):
        u"""Annulation du bon de carburant"""
        data_obj = self.pool.get('ir.model.data')
        for gasoil_order in self.browse(cr, uid, ids, context):
            if gasoil_order.state == 'done':
                result = self.pool.get('stock.move').create(cr, uid, {
                                'name': gasoil_order.name,
                                'product_id': gasoil_order.gasoil_id and gasoil_order.gasoil_id.id or False,
                                'product_uom_qty': -1 * gasoil_order.liter,
                                'product_uom': gasoil_order.gasoil_id.product_tmpl_id and gasoil_order.gasoil_id.product_tmpl_id.uom_id and gasoil_order.gasoil_id.product_tmpl_id.uom_id.id or False,
                                'location_id': gasoil_order.cistern_id and gasoil_order.cistern_id.id or False,
                                'location_dest_id': gasoil_order.location_id and gasoil_order.location_id.id or False,
                                'date': gasoil_order.date,
                                'state': 'done',
                                'note' : u'Annulation carburant',
                    })
                if result:
                    for gasoil_external in gasoil_order.assigned_external_ids:
                        self.pool.get('fleet.vehicle.log.fuel').write(cr, uid, [gasoil_external.id], {'state': 'draft'})
                            #self.pool.get('tms.gasoil.order.external').unhold(cr,uid,[gasoil_external.id],None)
                        #@TODO manage properly travel unassignement
                        #for read in self.read(cr,uid,ids,['assigned_travels_id','assigned_partial_travels_id']):
                        #    self.pool.get('tms.travel').unhold(cr,uid,read['assigned_travels_id'],None)
                        #    self.pool.get('tms.gasoil.order.partial').unlink(cr,uid,read['assigned_partial_travels_id'],None)
                    self.write(cr, uid, [gasoil_order.id], {'state': 'draft'})
                    #self.message_post(cr, uid, [gasoil_order.id], body=u"Le bon de carburant interne %s a été annulé."%(gasoil_order.name), context=context)
        return True

    def validate_external(self, cr, uid, ids, context):
        for record in self.browse(cr, uid, ids, context):
            if record.internal_order_id:
                self.write(cr, uid, [record.id], {'state': 'assigned'})
            else:
                self.write(cr, uid, [record.id], {'state': 'free'})
        return True

    def cancel_external(self, cr, uid, ids, context):
        self.write(cr, uid, ids, {'state': 'draft'})

    def _get_external_liter(self, cr, uid, ids, prop, unknow_none, context=None):
        u"""Litrage externe"""
        data={}
        for gasoil_order in self.browse(cr, uid, ids, context):
             liter = 0.0
             for gasoil_external in gasoil_order.assigned_external_ids:
                 liter = liter + gasoil_external.liter
             data[gasoil_order.id] = liter
        return data

    def _get_external_amount(self, cr, uid, ids, prop, unknow_none, context=None):
        u"""Montant HT externe"""
        data={}
        for gasoil_order in self.browse(cr, uid, ids, context):
             amount = 0.0
             for gasoil_external in gasoil_order.assigned_external_ids:
                 amount = amount + gasoil_external.amount
             data[gasoil_order.id] = amount
        return data

    def _get_real_consumption(self, cr, uid, ids, prop, unknow_none, context=None):
        u"""calcul de la consommation en %"""
        data={}
        for record in self.browse(cr, uid, ids, context):
            data[record.id] = (record.total_liter * 100.00 ) / (record.km_driven + 1)
        return data

    def _get_total_liter(self, cr, uid, ids, prop, unknow_none, context=None):
        u"""récupération du litrage (interne + externe)"""
        data={}
        for record in self.browse(cr, uid, ids, context):
            data[record.id] = record.liter + record.liter_external
        return data

    def _get_total_price(self, cr, uid, ids, prop, unknow_none, context=None):
        u"""calcul du prix"""
        data = {}
        for record in self.browse(cr, uid, ids, context):
            data[record.id] = (record.amount+record.amount_external) or 0.0
        return data

    _columns={
        'name':fields.char(u'N°', size=64, required=True, help=u"Numéro de bon carburant, par défaut numéroté"),
        'date_create': fields.datetime(u'Date d\'encodage', readonly=True, help="Date d'encodage du bon.", select=True, states={'done':[('readonly', True)]}),
        'date_order': fields.datetime(u'Date du bon', required=True, help="Date du bon.", select=True, states={'done':[('readonly', True)]}),
        'internal_order_id': fields.many2one('fleet.vehicle.log.fuel', u'Bon interne', required=False, domain="[('type','=','internal')]", help=u"Bon de carburant interne lié.", states={'done':[('readonly', True)]}),
        #'external_order_id': fields.many2one('fleet.vehicle.log.fuel', u'Bon externe'),
        #'station_id': fields.many2one('res.partner', u'Station/Fournisseur', domain=[('supplier','=',True)], states={'done':[('readonly', True)]}),
        'gasoil_id': fields.many2one('product.product', u'Gasoil', required=False, domain=[('gasoil_ok','=','True')], help=u"Carburant utilisé", states={'done':[('readonly', True)]}),
        'driver_id': fields.many2one('hr.employee', u'Chauffeur', domain=[('driver_ok','=',True)], help=u"Chauffeur affecté au véhicule, vous avez la possibilité de ne pas définir le chauffeur", states={'done':[('readonly', True)]}),
        'location_id': fields.many2one('stock.location', u'Local véhicule', required=True, help=u"Emplacement virtuel du véhicule", states={'done':[('readonly', True)]}), 
        'cistern_id': fields.many2one('stock.location', u'Citerne', required=False, domain=[('cistern_ok','=',True)], states={'done':[('readonly', True)]}),
        #'vehicle_id': fields.many2one('fleet.vehicle',u'Véhicule',required=True, domain="[('vehicle_ok','=','True')]",readonly=False),   
        'vehicle_code': fields.char(u'Référence véhicule', size=50, states={'done':[('readonly', True)]}),
        'qty_stock': fields.float(u'Stock', digits=(16,2), states={'done':[('readonly', True)]}),
        'location_id': fields.many2one('stock.location', u'Local véhicule', required=False, help=u"Emplacement virtuel du véhicule", states={'done':[('readonly', True)]}),
        'system_number': fields.char(u'Numero système', size=64, help=u"Numéro du système si vous identifiez avec une méthode tierce vos approvisionnements en carburant.", states={'done':[('readonly', True)]}),
        #'month': fields.function(_get_month,type='char',method=True,string=u"Mois"),
        #'date': fields.datetime(u'Date du bon',required=True),
        'company_id': fields.many2one('res.company', u'Compagnie', readonly=True, required=True),
        'attendant_id': fields.many2one('hr.employee', u'Pompiste', required=False, readonly=False, domain=[('attendant_ok','=',True)], help=u"Pompiste effectuant l'approvisionnement du carburant.", states={'done':[('readonly', True)]}),
        'user_id': fields.many2one('res.users', u'Responsable', readonly=True, help=u"Utilisateur qui a saisi le bon de carburant"),
        #'assigned_travels_id': fields.one2many('tms.travel','gasoil_order',u'Voyages assignés au bon',ondelete="set null",help=u"Sélectionnez les voyages effectués avec ce bon pour un contrôle adéquat de la consommation"),
        #'assigned_partial_travels_id': fields.one2many('tms.gasoil.order.partial','gasoil_order',u'Voyages partiels',help=u"Sélectionnez les voyages effectués avec plusieurs bons dont ce bon pour un contrôle adéquat de la consommation"),
        'assigned_external_ids': fields.one2many('fleet.vehicle.log.fuel', 'internal_order_id', u'bon de carburant externe assigné', domain=[('type','=','external')], states={'done':[('readonly', True)]}, ondelete="set null", help=u"Sélectionnez les bons de carburant externe effectués avec ce bon pour un contrôle adéquat de la consommation."),
        'counter_old': fields.float(u'Ancien compteur', readonly=False, required=True, help=u"L'ancien compteur du véhicule au moment de la saisie du bon", states={'done':[('readonly', True)]}),      
        #'counter_new_computed': fields.function(_get_counter, method=True, type="float", string=u"Nouveau Compteur réalisé calculé",help=u"Nouveau compteur calculé sur base de l'ancien compteur saisie et des km parcourus renseignés dans la liste des voyages affectés aux bons"),
        'counter_new': fields.float(u'Nouveau compteur', required=True,help=u"Nouveau compteur à prélever sur le véhicule au moment de la saisie du bon", states={'done':[('readonly', True)]}),
        'consumption_gasoil': fields.related('vehicle_id','consumption_gasoil',string=u'Consommation moyenne du véhicule(%)', type="float", readonly=True, store=True, help=u"Consommation en % définie dans la fiche véhicule", states={'done':[('readonly', True)]}),
        'km_driven': fields.float(u"Total km. parcourus", help=u"Nouveau compteur - Ancien compteur", states={'done':[('readonly', True)]}),
        'amount_ttc': fields.float(u'Montant TTC', digits_compute= dp.get_precision(u'Montant carburant')),
        'tax_ids': fields.many2many('account.tax', 'log_fuel_picking_tax', 'log_fuel_id', 'tax_id', u'Taxes', states={'done':[('readonly', True)]}),
        #'assigned_ok': fields.boolean(u'Assigné'),
        #'total_km_driven_computed':fields.function(_amount_all, method=True, type="float", string=u"Kilomètres parcourus calculés", help=u"nouveau compteur calculé - ancien compteur", multi='sums',store={
        #        'tms.gasoil.order': (lambda self, cr, uid, ids, c={}: ids, ['assigned_external_gasoil_order_id','assigned_travels_id'], 10),
        #        'tms.travel': (_get_travel_order, None, 10),
        #        'tms.gasoil.order.partial': (_get_travel_partial_order, None, 10),
        #        'tms.gasoil.order.external': (_get_gasoil_external_order, None, 10),
        #        }, ),
        #'amount_travel_total':fields.function(_amount_all, method=True, type="float", string=u"Montant total voyages", digits_compute= dp.get_precision(u'Montant Total'), multi='sums',store={
        #        'tms.gasoil.order': (lambda self, cr, uid, ids, c={}: ids, ['assigned_external_gasoil_order_id','assigned_travels_id'], 10),
        #        'tms.travel': (_get_travel_order, None, 10),
        #        'tms.gasoil.order.partial': (_get_travel_partial_order, None, 10),
        #        'tms.gasoil.order.external': (_get_gasoil_external_order, None, 10),
        #        }),
        'liter_external': fields.function(_get_external_liter, method=True, string=u'Litrage externe réalisé', type='float'),
        'amount_external': fields.function(_get_external_amount, method=True, digits_compute=dp.get_precision(u'Montant carburant'), string=u'Montant externe HT', type='float'),
        #'amount_external_ttc': fields.function(_get_external_amount, method=True, string=u'Montant externe TTC', type='float'),
        'total_real_consumption': fields.function(_get_real_consumption, method = True, string = u'Consommation Totale réelle(%)', type = 'float', help=u"(Total litrage réalisé * 100)/ Kilométrage parcourus" ),
        #'total_intern_liter': fields.float(u'Litrage réalisé (Interne)', digits=(16,2),required=True,help=u"Litrage à prélever dans la cuve gasoil", states={'done':[('readonly', True)]}),
        'total_liter': fields.function(_get_total_liter, method=True, string=u'Total litrage réalisé', type='float', help=u"Litrage réalisé (Interne) + Litrage réalisé (Externe)"),
        #'total_liter_estimated': fields.function(_amount_all,method = True, string = u'Total litrage estimé', type = 'float',help=u"Litrage estimé (Interne) + Litrage realise (Externe)"  , multi='sums',store={
        #        'tms.gasoil.order': (lambda self, cr, uid, ids, c={}: ids, ['assigned_external_gasoil_order_id','assigned_travels_id'], 10),
        #        'tms.travel': (_get_travel_order, None, 10),
        #        'tms.gasoil.order.partial': (_get_travel_partial_order, None, 10),
        #        'tms.gasoil.order.external': (_get_gasoil_external_order, None, 10),
        #        },),            
        #'total_external_liter': fields.function(_amount_all, method=True, type = 'float', string=u'total litrage Gasoil Externe.', multi='sums',help=u"Litrage externe sur base des bons carburants externes sélectionnés",store={
        #        'tms.gasoil.order': (lambda self, cr, uid, ids, c={}: ids, ['assigned_external_gasoil_order_id','assigned_travels_id'], 10),
        #        'tms.travel': (_get_travel_order, None, 10),
        #        'tms.gasoil.order.partial': (_get_travel_partial_order, None, 10),
        #        'tms.gasoil.order.external': (_get_gasoil_external_order, None, 10),
        #        },),
        'total_price': fields.function(_get_total_price, method=True, digits_compute=dp.get_precision(u'Montant carburant'), string = u'Prix total (HT)', type = 'float', help=u'Prix HT interne + Prix HT externe'),
        #'variance_liter': fields.function(_get_variance_liter,method = True, string = u'Différence litrage  ', type = 'float', help=u"Total litrage réalisé -Total litrage estimé " ),
        #'variance_km': fields.function(_get_variance_km,method = True, string = u'Différence km', type = 'float', help=u"Total km réalisé -Total km estimé " ),
        #'total_km_estimated': fields.function(_amount_all, method=True,type = 'float', digits=(16,3), string=u'Total Kilometrage Estim.', multi='sums',help=u"KM des voyages sans km supplémentaires",
          #                                    store={
         #       'tms.gasoil.order': (lambda self, cr, uid, ids, c={}: ids, ['assigned_external_gasoil_order_id','assigned_travels_id'], 10),
         #       'tms.travel': (_get_travel_order, None, 10),
         #       'tms.gasoil.order.partial': (_get_travel_partial_order, None, 10),
         #       'tms.gasoil.order.external': (_get_gasoil_external_order, None, 10),
         #   },
        #                                       ), 
        #'total_autoroute_cost': fields.function(_amount_all, method=True, type = 'float', digits=(16,3), string=u'Total Frais Auto-Route', multi='sums',help=u"Frais autoroutes sur base des voyages sélectionnés",
        #                                        store={
        #        'tms.gasoil.order': (lambda self, cr, uid, ids, c={}: ids, ['assigned_external_gasoil_order_id','assigned_travels_id'], 10),
        #        'tms.travel': (_get_travel_order, None, 10),
        #        'tms.gasoil.order.partial': (_get_travel_partial_order, None, 10),
        #        'tms.gasoil.order.external': (_get_gasoil_external_order, None, 10),
        #    }, ),
        #'total_autoroute_cost_estimated': fields.function(_amount_all, method=True,type = 'float', digits=(16,3), string=u'Total Frais Auto-Route estimé', multi='sums',help=u"Frais autoroutes sans frais supplémentaires",
        #                                                  store={
        #        'tms.gasoil.order': (lambda self, cr, uid, ids, c={}: ids, ['assigned_external_gasoil_order_id','assigned_travels_id'], 10),
        #        'tms.travel': (_get_travel_order, None, 10),
        #        'tms.gasoil.order.partial': (_get_travel_partial_order, None, 10),
        #        'tms.gasoil.order.external': (_get_gasoil_external_order, None, 10),
        #    }, ),
        'type': fields.selection([('internal', u'Interne'), ('external', u'Externe')], u'Type', states={'done':[('readonly', True)]}),
        'state': fields.selection([
            ('info', u'Encodage'),
            ('draft', u'Brouillon'),
            #('confirmed', u'Traitement'),
            ('assigned', u'Assigné'),
            ('free', u'Libre'),
            ('done', u'Validé'),
            ('cancel', u'Annulé')
            ], u'Etat', readonly=True, select=True),
        'category_id': fields.many2one('fleet.vehicle.category', u'Catégorie', states={'done':[('readonly', True)]}),
        'payment_type': fields.selection([('card', u'Carte'),('nature', u'Espèces')], u'Type de paiement'),
        'station_site': fields.char(u"Site/Ville", size=64),
        'price_per_liter': fields.float(u'Prix au litre', digits_compute=dp.get_precision(u'Prix carburant')),
        'amount': fields.float(u'Prix Total', digits_compute=dp.get_precision(u'Montant carburant')),
        'owner': fields.char(u'Propriétaire', size=32),
        'manager': fields.char(u'Exploitant', size=32),
        }

    def _get_tms_default_service_type(self, cr, uid, context):
        fuel_type=context.get('default_type', "")
        module = fuel_type and 'tms' or 'fleet'
        service_type = fuel_type and ('type_service_refueling_'+fuel_type) or ('type_service_refueling')
        model, model_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, module, service_type)
        return model_id

    _defaults = {
        'cost_subtype_id': _get_tms_default_service_type,
        'date_order': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'payment_type': lambda *a: 'nature',
        #'state': lambda *a: 'info',
        'name': lambda self, cr, uid, context: '/',
        'counter_old': lambda *a: 0.0,
        'counter_new': lambda *a: 0.0,
        #'total_intern_liter': lambda *a: 0.0,
        #'price_fuel' : lambda *a: 0.0,
        'qty_stock' : lambda *a: 0.0,
        'amount_ttc' : lambda *a: 0.0,
        'date': lambda *a : time.strftime('%Y-%m-%d %H:%M:%S'),
        'user_id': lambda self, cr, uid, ctx: uid,
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'fleet.vehicle.log.fuel', context=c),
        }

    def onchange_internal_order_id(self, cr, uid, ids, internal_order_id, context={}):
        u"""évènement lors du changement du type"""
        data={}
        if internal_order_id:
            gasoil_order = self.pool.get('fleet.vehicle.log.fuel').browse(cr, uid, internal_order_id, context=context)
            data = {
                     'vehicle_code': gasoil_order.vehicle_code or "",
                     'vehicle_id': gasoil_order.vehicle_id and gasoil_order.vehicle_id.id or False,
                     'driver_id': gasoil_order.driver_id and gasoil_order.driver_id.id or False,
                    }
        return {'value': data}

    def onchange_order_type(self, cr, uid, ids, type, context={}):
        u"""évènement lors du changement du type"""
        data={}
        if type:
            data = {'cost_subtype_id': self._get_tms_default_service_type(cr, uid, context={'default_type': type})}
        return {'value': data}


    def onchange_vehicle_code(self, cr, uid, ids, code, context={}):
        u"""évènement lors du changement du code véhicule"""
        data={}
        if code:
            vehicle_ids = self.pool.get('fleet.vehicle').search(cr, uid, [('default_code','=',code),('vehicle_ok','=',True)])
            if vehicle_ids:
                vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_ids[0])
                data['vehicle_id'] = vehicle and vehicle.id or False
        return {'value': data}

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id, context={}):
        if not vehicle_id:
            return {}
        vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
        driver_id = vehicle.hr_driver_id and vehicle.hr_driver_id.id or False
        owner = vehicle.owner or "" #and vehicle.owner_id.id or False
        manager = vehicle.manager or "" # and vehicle.manager_id.id or False
        category_id = vehicle.category_id and vehicle.category_id.id or False
        location_id = vehicle.location_id and vehicle.location_id.id or False
        counter_old = vehicle.fuel_odometer or 0.0
        default_code = vehicle.default_code
        odometer_unit = vehicle.odometer_unit
        #consumption_gasoil = vehicle.consumption_gasoil
        data = {
            'driver_id': driver_id,
            'owner': owner,
            'manager': manager,
            'category_id': category_id,
            'location_id': location_id,
            'counter_old': counter_old,
            'vehicle_code': default_code,
            'odometer_unit': odometer_unit,
            }
        return {'value': data}

    def onchange_gasoil_id(self, cr, uid, ids, gasoil_id, context=None):
        u"""évènement lors du changement du carburant"""
        data={}
        gasoil = self.pool.get('product.product').browse(cr, uid, gasoil_id)
        if gasoil.standard_price:
            data['price_per_liter'] = gasoil.standard_price
            data['qty_stock'] = gasoil.qty_available or 0.0
        return {'value' : data}

    def onchange_counter_new(self, cr, uid, ids, counter_old, counter_new, context={}):
        result = {'fuel_odometer': 0.0, 'km_driven': 0.0}
        warning = {}
        if counter_new:
            counter_diff = counter_new - counter_old
            if counter_diff < 0:
                warning = {'title': u'Attention !', 'message': u'Le nouveau compteur ne peut pas être inférieur à l\'ancien compteur.'}
            else:
                result.update({'fuel_odometer': counter_new, 'km_driven': counter_diff})
        return {'value': result, 'warning': warning}

    def on_change_liter(self, cr, uid, ids, liter, price_per_liter, amount, context=None):
        #need to cast in float because the value receveid from web client maybe an integer (Javascript and JSON do not
        #make any difference between 3.0 and 3). This cause a problem if you encode, for example, 2 liters at 1.5 per
        #liter => total is computed as 3.0, then trigger an onchange that recomputes price_per_liter as 3/2=1 (instead
        #of 3.0/2=1.5)
        #If there is no change in the result, we return an empty dict to prevent an infinite loop due to the 3 intertwine
        #onchange. And in order to verify that there is no change in the result, we have to limit the precision of the 
        #computation to 2 decimal
        liter = float(liter)
        amount = float(amount)
        price_per_liter = float(price_per_liter)
        price_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Prix carburant')
        amount_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant carburant')
        if liter > 0 and price_per_liter > 0 and round(liter*price_per_liter,amount_prec) != amount:
            return {'value' : {'amount' : round(liter * price_per_liter,amount_prec),}}
        #elif amount > 0 and liter > 0 and round(amount/liter,price_prec) != price_per_liter:
         #   return {'value' : {'price_per_liter' : round(amount / liter,price_prec),}}
        elif amount > 0 and price_per_liter > 0 and round(amount/price_per_liter,2) != liter:
            return {'value' : {'liter' : round(amount / price_per_liter,2),}}
        else :
            return {}

    def on_change_price_per_liter(self, cr, uid, ids, liter, price_per_liter, amount, context=None):
        #need to cast in float because the value receveid from web client maybe an integer (Javascript and JSON do not
        #make any difference between 3.0 and 3). This cause a problem if you encode, for example, 2 liters at 1.5 per
        #liter => total is computed as 3.0, then trigger an onchange that recomputes price_per_liter as 3/2=1 (instead
        #of 3.0/2=1.5)
        #If there is no change in the result, we return an empty dict to prevent an infinite loop due to the 3 intertwine
        #onchange. And in order to verify that there is no change in the result, we have to limit the precision of the 
        #computation to 2 decimal
        liter = float(liter)
        amount = float(amount)
        price_per_liter = float(price_per_liter)
        price_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Prix carburant')
        amount_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant carburant')
        if liter > 0 and price_per_liter > 0 and round(liter*price_per_liter,amount_prec) != amount:
            return {'value' : {'amount' : round(liter * price_per_liter,amount_prec),}}
        elif amount > 0 and price_per_liter > 0 and round(amount/price_per_liter,2) != liter:
            return {'value' : {'liter' : round(amount / price_per_liter,2),}}
        #elif amount > 0 and liter > 0 and round(amount/liter,price_prec) != price_per_liter:
         #   return {'value' : {'price_per_liter' : round(amount / liter,price_prec),}}
        else :
            return {}

    def on_change_amount_external(self, cr, uid, ids, liter, price_per_liter, amount, amount_ttc, tax_ids, context=None):
        #need to cast in float because the value receveid from web client maybe an integer (Javascript and JSON do not
        #make any difference between 3.0 and 3). This cause a problem if you encode, for example, 2 liters at 1.5 per
        #liter => total is computed as 3.0, then trigger an onchange that recomputes price_per_liter as 3/2=1 (instead
        #of 3.0/2=1.5)
        #If there is no change in the result, we return an empty dict to prevent an infinite loop due to the 3 intertwine
        #onchange. And in order to verify that there is no change in the result, we have to limit the precision of the 
        #computation to 2 decimal
        value={}
        liter = float(liter)
        amount = float(amount)
        amount_ttc = float(amount_ttc)
        price_per_liter = float(price_per_liter)
        tax_obj = self.pool.get('account.tax')
        amount_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant carburant')
        price_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Prix carburant')
        tax_list = [tax[2][0] for tax in tax_ids if tax[2]]
        new_price_per_liter = liter and round(amount / liter, price_prec) or 0.0
        new_liter = new_price_per_liter and round(amount/new_price_per_liter,2) or 0.0
        if tax_list and amount > 0 and price_per_liter > 0 and liter > 0 :
            taxes = tax_obj.compute_all(cr, uid, tax_obj.browse(cr, uid, tax_list, context=context), new_price_per_liter, new_liter)
            if amount_ttc != taxes['total_included']:
                value = {'amount_ttc': taxes['total_included'],}
        elif amount > 0 and price_per_liter > 0 and new_liter != liter:
            value.update({'liter': new_liter,})
            return {'value': value}
        elif liter > 0 and price_per_liter > 0 and round(liter*price_per_liter,amount_prec) != amount:
            value.update({'amount': round(liter * price_per_liter,amount_prec),})
            return {'value': value}
        else :
            return {'value': value}

    def on_change_amount_ttc_external(self, cr, uid, ids, liter, price_per_liter, amount, amount_ttc, tax_ids, context=None):
        value={}
        liter = float(liter)
        amount = float(amount)
        amount_ttc = float(amount_ttc)
        price_per_liter = float(price_per_liter)
        tax_obj = self.pool.get('account.tax')
        new_amount=amount_ttc
        amount_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant carburant')
        price_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Prix carburant')
        tax_list = [tax[2][0] for tax in tax_ids if tax[2]]
        new_price_per_liter = liter and round(new_amount / liter, price_prec) or 0.0
        new_liter = new_price_per_liter and round(new_amount/new_price_per_liter,2) or 0.0
        if tax_list and amount > 0 and price_per_liter > 0 and liter > 0 :
            taxes = tax_obj.compute_all(cr, uid, tax_obj.browse(cr, uid, tax_list, context=context), new_price_per_liter, new_liter)
            if amount_ttc != taxes['total_included']:
                value = {'amount_ttc': taxes['total_included'],}
        if amount > 0 and liter > 0 and new_price_per_liter != price_per_liter:
            value.update({'price_per_liter': new_price_per_liter,})
            return {'value': value}
        elif amount > 0 and price_per_liter > 0 and new_liter != liter:
            value.update({'liter': new_liter,})
            return {'value': value}
        elif liter > 0 and price_per_liter > 0 and round(liter*price_per_liter,2) != amount:
            value.update({'amount': round(liter * price_per_liter,2),})
            return {'value': value}
        else :
            return {'value': value}

    def onchange_gasoil_id_external(self, cr, uid, ids, prod_id=False, station_id=False, product_qty=0):
        price=0
        warning = {}
        result={}
        if not station_id:
            raise osv.except_osv(u'Fournisseur non défini !', u'Prière de selectionner un fournisseur pour l\'encodage du bon externe.')
        partner_id=self.pool.get('res.partner').browse(cr,uid,station_id)
        result.update({'station_site': partner_id.city or ""})
        if not prod_id:
            return {'value': result}
        lang = False
        #if len(partner_id.address) == 0:
        #    raise osv.except_osv(u'Addresse fournisseur non définie !', u'Prière de selectionner un fournisseur avec une addresse.')
        ctx = {'lang': lang}
        product = self.pool.get('product.product').browse(cr, uid, [prod_id], context=ctx)[0]
        product_obj = self.pool.get('product.product').browse(cr, uid, prod_id,None)
        if product_obj:
            result['price_per_liter'] = float(product_obj.standard_price) or 0.0
            result['tax_ids'] = [x.id for x in product_obj.supplier_taxes_id]
            #commission
            if partner_id:
                pricelist_lst=partner_id.property_product_pricelist_purchase
                if pricelist_lst:
                    pricelist = partner_id.property_product_pricelist_purchase and partner_id.property_product_pricelist_purchase.id or False
                    if pricelist:
                        price=self.pool.get('product.pricelist').price_get(cr, uid, [pricelist], prod_id, product_qty, partner_id.id)[pricelist]
                        result['price_per_liter']=float(price)
                        if not result['price_per_liter']:
                            warning = {
                                'title': u'Carburant sans prix !',
                                'message': u'Ce carburant ne possède pas de prix standard et n\'est lié à aucune liste de prix de ce fournisseur.',
                                }
        return {'value': result, 'warning': warning}

fleet_vehicle_log_fuel()
