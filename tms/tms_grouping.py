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
from openerp import netsvc
from openerp.osv import fields, osv
from openerp.tools.translate import _
from datetime import datetime
import time
import openerp.addons.decimal_precision as dp

__author__ = "NEXTMA"
__version__ = "0.1"
#__date__ = "07 Février 2014"

class tms_grouping(osv.osv):
    _name='tms.grouping'
    _description=u'Groupage des BLs'

    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tms.grouping') or '/'
        return super(tms_grouping, self).create(cr, uid, vals, context=context)

    def action_cancel(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state': 'cancel'})
        return True

    def action_assign(self, cr, uid, ids, context=None):
        for group in self.browse(cr,uid,ids,context):
            pick_ids = [pick.id for pick in group.picking_ids]
            self.pool.get('tms.picking').force_assign(cr, uid, pick_ids)
        self.write(cr, uid, ids, {'state': 'assigned'})
        return True

    def action_done(self, cr, uid, ids, context=None):
        for group in self.browse(cr,uid,ids,context):
            pick_ids = [pick.id for pick in group.picking_ids]
            if group.state == 'draft':
                self.pool.get('tms.picking').draft_force_done(cr, uid, pick_ids)
            else:
                wf_service = netsvc.LocalService("workflow")
                for pick_id in pick_ids:
                    wf_service.trg_validate(uid, 'tms.picking', pick_id, 'button_done', cr)
            res_create = self.pool.get('tms.travel').create(cr, uid, {
                         'grouping_id': group.id,
                         'date': group.date or False,
                         'name': group.name or "",
                         'vehicle_code': group.vehicle_code or "",
                         'product_id': group.traject_id and group.traject_id.id or False,
                         'vehicle_id': group.vehicle_id and group.vehicle_id.id or False,
                         'trailer_id': group.trailer_id and group.trailer_id.id or False,
                         'driver_id': group.driver_id and group.driver_id.id or False,
                         'amount_total_ht': group.amount_total_ht or 0.0,
                         'amount_total': group.amount_total or 0.0,
                         'freeway_total': group.freeway_total or 0.0,
                         'km_total': group.km_total or 0.0,
                         }, {'travel_ok': True})
        self.write(cr, uid, ids, {'state': 'done'})
        return True

    def _get_picking_datas(self, cr, uid, ids, prop, unknow_none, context):
        u"""Informations sur les BLs"""
        data={}
        for record in self.browse(cr, uid, ids, context):
            truck_actual_charge = 0.0
            amount_total_ht = 0.0
            amount_total = 0.0
            commission = 0.0
            for pick in record.picking_ids:
                commission += pick.commission
                amount_total_ht += pick.amount_total_ht
                amount_total += pick.amount_total
                truck_actual_charge += pick.delivrery_qty
            data[record.id]={
                'truck_actual_charge': truck_actual_charge,
                'amount_total_ht': amount_total_ht,
                'amount_total': amount_total,
                #'km_total': 0.0,
                #'freeway_total': 0.0,
                'commission': commission,
                }
        return data

    def _get_total(self, cr, uid, ids, prop, unknow_none, context):
        u"""calcul du total du km et des frais d'autoroute"""
        data={}
        if ids:
            for record in self.read(cr, uid, ids, ['km_estimated', 'km_additional', 'freeway_estimated', 'freeway_additional'], context):
                data[record['id']]={
                                    'km_total' : 0.0,
                                    'freeway_total' : 0.0,
                                    }
                data[record['id']]['km_total'] = (record['km_estimated'] + record['km_additional']) or 0.0
                data[record['id']]['freeway_total'] = (record['freeway_estimated'] + record['freeway_additional']) or 0.0
        return data

    _columns={
        'name': fields.char(u'Nom', size=32, required=True),
        'circuit_id': fields.many2one('tms.grouping.circuit', u'Circuit', required=False, help="Circuit de clients et de trajets pour faciliter la saisie des BLs."),
        'truck_max_charge': fields.float(u'Charge maximale autorisée', help=u"Charge maximale pour un camion sur ce circuit."),
        'charge_uom_id': fields.many2one('product.uom', u'Unité de livraison', required=False, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help=u"Unité de mesure de la charge, i.e: tonne."),
        'truck_actual_charge': fields.function(_get_picking_datas, method=True, string=u'Charge actuelle', type='float', readonly=True, multi='sums1'),
        'commission': fields.function(_get_picking_datas, method=True, string=u'Commission totale', type='float', readonly=True, multi='sums1'),
        'amount_total_ht': fields.function(_get_picking_datas, method=True, string=u'Montant total HT', type='float', readonly=True, multi='sums1'),
        'amount_total': fields.function(_get_picking_datas, method=True, string=u'Montant total TTC', type='float', readonly=True, multi='sums1'),
        'km_estimated': fields.float(u'Km estimé', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'km_additional': fields.float(u'Km supplémentaire', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        #'km_total': fields.float(u'Km total', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'km_total': fields.function(_get_total, method=True, string = u'Km total', type='float', multi='sums2', readonly=True, store=True),
        'freeway_estimated': fields.float(u'Autoroute estimée', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'freeway_additional': fields.float(u'Autoroute supplémentaire', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'freeway_total': fields.function(_get_total, method=True, string=u'Autoroute total', type='float', multi='sums2', readonly=True, store=True),
        #'freeway_total': fields.float(u'Autoroute total', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        #'km_total': fields.function(_get_picking_datas, method=True, string=u'Km total', type='float', readonly=True, multi='sums1'),
        #'freeway_total': fields.function(_get_picking_datas, method=True, string=u'Autoroute total', type='float', readonly=True, multi='sums1'),
        'picking_ids': fields.one2many('tms.picking', 'grouping_id', u'Lignes de livraison',states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'user_id': fields.many2one('res.users', u'Responsable', readonly=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'vehicle_id' : fields.many2one('fleet.vehicle', string=u"Véhicule", required=True, domain=[('vehicle_ok','=',True)], states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'vehicle_code': fields.char(u'Référence véhicule', size=50, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'driver_id': fields.many2one('hr.employee', string=u"Chauffeur", required=True, domain="[('driver_ok','=','True')]", help=u"Chauffeur dédié pour ce groupage.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'trailer_id' : fields.many2one('fleet.vehicle', string=u"Semi-remorque", domain=[('trailer_ok','=',True)], help=u"Semi-remorque dédiée pour ce voyage.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        #'company_id': fields.many2one('res.company', u'Compagnie', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'note': fields.text('Notes', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'state': fields.selection([
            ('draft', u'Brouillon'),
            ('cancel', u'Annulé'),
            ('confirmed', u'Plannifié'),
            ('assigned', u'Assigné'),
            ('done', u'Terminé'),
            ], u'Etat', readonly=True, select=True, track_visibility='onchange', help="""
            * Brouillon: Bons de livraison voyage non encore confirmés.\n
            * En attente de disponibilité: En attente de disponibilité du véhicule ou du chauffeur pour effectuer les voyages.\n
            * Assigné: Véhicule et chauffeur assignés, juste en attente de la validation de l'utilisateur.\n
            * Terminé: Voyages créés, bons de livraison validés et prêts à être facturés.\n
            * Annulé: Les livraisons ont été annulées."""
        ),
        'date': fields.datetime(u'Date voyage', required=True, help=u"Date de début du voyage", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'tms_journal_id': fields.many2one('tms.journal', u'Journal TMS', select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'trajet_ok': fields.boolean(u'Trajet ?', help=u"Cocher pour définir un plus long trajet pour le groupage, manuellement ou décocher pour choisir un circuit.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'traject_id': fields.many2one('product.product', u'Trajet', domain="[('trajet_ok','=',True)]", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        #'generate_ok': fields.boolean(u'Encodage'),
        }

    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'state': 'draft',
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        #'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'tms.picking', context=c),
        'user_id': lambda obj, cr, uid, context: uid,
        'trajet_ok': True,
        #'generate_ok': lambda obj, cr, uid, context: context.get('generate_ok', False),
        }

    def onchange_vehicle_code(self, cr, uid, ids, code, context={}):
        u"""évènement lors du changement du code véhicule"""
        data={}
        if code:
            vehicle_ids = self.pool.get('fleet.vehicle').search(cr, uid, [('default_code','=',code),('vehicle_ok','=',True)])
            if len(vehicle_ids):
                vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_ids[0])
                data['vehicle_id'] = vehicle and vehicle.id or False
        return {'value': data}

    def onchange_traject_id(self, cr, uid, ids, traject_id, context=None):
        u"""évènement lors du changement du trajet"""
        data = {}
        if traject_id:
            traject = self.pool.get('product.product').browse(cr, uid, traject_id, context=context)
            if traject:
                data['freeway_estimated'] = traject.freeway_estimated or 0.0
                data['km_estimated'] = traject.km_estimated or 0.0
        return {'value' : data}

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id, context=None):
        u"""évènement lors du changement du véhicule"""
        data = {}
        if vehicle_id:
            vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
            if vehicle:
                data['driver_id'] = vehicle.hr_driver_id and vehicle.hr_driver_id.id or False
                data['vehicle_code'] = vehicle.default_code
                data['trailer_id'] = vehicle.trailer_id and vehicle.trailer_id.id or False
        return {'value' : data}

    def onchange_circuit_id(self, cr, uid, ids, circuit_id, context=None):
        u"""évènement lors du changement du circuit"""
        data = {}
        if circuit_id:
            circuit = self.pool.get('tms.grouping.circuit').browse(cr, uid, circuit_id, context=context)
            if circuit:
                #print "\n circuit charge_uom_id", circuit.charge_uom_id.id
                data.update({'charge_uom_id': circuit.charge_uom_id and circuit.charge_uom_id.id, 'truck_max_charge': circuit.truck_max_charge})
        return {'value' : data}

tms_grouping()

class tms_grouping_circuit(osv.osv):
    _name='tms.grouping.circuit'
    _description=u'Circuits de clients'

    def _get_total_km(self, cr, uid, ids, prop, unknow_none, context):
        u"""Calcul du total du km"""
        data={}
        for record in self.browse(cr, uid, ids, context):
            data[record.id]=0.0
        return data

    _columns={
        'name': fields.char(u'Nom du circuit', size=64, required=True),
        'truck_max_charge': fields.float(u'Charge maximale permise', help=u"Charge maximale pour un camion sur ce circuit.", required=True),
        'charge_uom_id': fields.many2one('product.uom', u'Unité de mesure', help=u"Unité de mesure de la charge, i.e: tonne.", required=True),
        #'product_ids': fields.one2many('product.product', 'circuit_id', u'Marchandises transportées', domain="[('picking_product_ok','=',True)]", help=u"Marchandises transportées sur ce circuit."),
        'total_km': fields.function(_get_total_km, method=True, string = u'Km total', type='float', readonly=True, store=True),
        'circuit_line_ids': fields.one2many('tms.grouping.circuit.line', 'circuit_id', u'Itinéraire'),
        }

    _defaults={
        }

    _sql_constraints = [
        ('tms_circuit_name_uniq', 'unique(name)', u'Le nom du circuit doit être unique !')
    ]

tms_grouping_circuit()

class tms_grouping_circuit_line(osv.osv):
    _name='tms.grouping.circuit.line'
    #_description=u'Itinéraires'
    _order='sequence asc'

    _columns={
        'circuit_id': fields.many2one('tms.grouping.circuit', u'id circuit'),
        'sequence': fields.integer(u'Séquence', required=True),
        'partner_id': fields.many2one('res.partner', u'Client', required=True),
        #'partner_ids': fields.many2many('res.partner', 'tms_circuit_line_partner', 'circuit_line_id', 'partner_id', u'Clients', required=True, domain="[('customer','=',True)]"),
        'traject_id': fields.many2one('product.product', u'Trajet', domain="[('trajet_ok','=',True)]", required=True),
        }

    _defaults={
        'sequence': 0,
        }

    _sql_constraints = [
        ('tms_circuit_line_traject_partner_uniq', 'unique(circuit_id,traject_id,partner_id)', u'Vous ne pouvez définir deux itinéraires du même couple (trajet, client) !')
    ]

tms_grouping_circuit_line()
