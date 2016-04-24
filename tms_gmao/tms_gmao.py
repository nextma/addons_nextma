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
import datetime
from openerp.osv import fields, osv
from openerp.tools.translate import _
import time

__author__ = "NEXTMA"
__version__ = "0.1"
__date__ = u"21 Janvier 2014"

class tms_gmao_pm(osv.Model):
    u"""Maintenance préventive"""
    _name = "tms.gmao.pm"
    _inherit = 'mail.thread'
    _description = u"Maintenance préventive"
    _order="create_date desc"

    def unlink(self, cr, uid, ids, context=None):
        u"""Méthode de suppression"""
        raise osv.except_osv(u'Suppression impossible', u'Vous ne pouvez pas supprimer une maintenance programmée, songez à l\'annuler')
        return super(tms_gmao_pm, self).unlink(cr, uid, ids, context)

    def _get_type_alert(self, cr, uid, ids, prop, unknow_none, context):
        u"""Type d'alerte"""
        res = {}
        if ids:
            reads = self.browse(cr, uid, ids, context)
            for record in reads:  
                res[record.id] = record.service_type_id and record.service_type_id.name or ''
        return res

    def _get_information_alert(self, cr, uid, ids, prop, unknow_none, context={}):
        u"""Récupérer les données des alertes"""
        res = {}
        if ids:
            reads = self.browse(cr, uid, ids, context)
            for record in reads:
                res[record.id]={
                                'days_next_due': False,
                                'days_left': 0,
                                'km_next_due': 0,
                                'km_left': 0,
                                'state': 'draft',
                                }
                ids_alert = self.pool.get('tms.gmao.pm.alert').search(cr,uid,[('pm_id','=',record.id),('state_process','=','progress')])
                if ids_alert:
                    ids_alert.sort(reverse=True)
                    last_object_alert_pm = self.pool.get('tms.gmao.pm.alert').browse(cr,uid,ids_alert[0])
                    if last_object_alert_pm:
                        if record.meter == 'days':
                            res[record.id]['days_next_due']= last_object_alert_pm.days_next_due
                            res[record.id]['days_left']= last_object_alert_pm.days_left
                        if record.meter== 'km':
                            res[record.id]['km_next_due']= last_object_alert_pm.km_next_due
                            res[record.id]['km_left']= last_object_alert_pm.km_left
                        res[record.id]['state']= last_object_alert_pm.state
                else:
                    nbr_alert=self.pool.get('tms.gmao.pm.alert').search_count(cr,uid,[('pm_id','=',record.id)])
                    if nbr_alert:
                        res[record.id]['state']= u'done'
        return res

    def _get_counter_current(self, cr, uid, ids, prop, unknow_none, context={}):
        u"""Calcul du compteur courant"""
        res = {}
        if ids:
            reads = self.browse(cr, uid, ids, context)
            for record in reads:
                if record.vehicle_id:
                    if record.vehicle_id.vehicle_ok:
                        if self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_current_counter'], context)['tms_gmao_param_current_counter'] == False:
                            res[record.id] = record.vehicle_id.fuel_odometer
                        else:
                            res[record.id] = record.vehicle_id.odometer
                    else:
                        res[record.id] = record.vehicle_id.odometer
        return res

    def end_periodic(self, cr, uid, ids, context={}):
        if ids:
            self.write(cr, uid, ids, {'periodic': False})
        return True

    def end_pm(self, cr, uid, ids, context={}):
        if ids:
            for object_pm in self.browse(cr, uid, ids):
                self.write(cr, uid, ids, {'periodic': False})
                ids_search_pm_alert = self.pool.get('tms.gmao.pm.alert').search(cr, uid, [('pm_id','=',object_pm.id),('state_process','=','progress')])
                if ids_search_pm_alert:
                    self.pool.get('tms.gmao.pm.alert').action_cancel_alert(cr, uid, ids_search_pm_alert)
        return True

    def generate_alert(self,cr,uid,ids,context={}):
        u"""Générer l'alerte"""
        if ids:
            for object_pm in self.browse(cr,uid,ids):
                data={}
                if object_pm.meter == 'km':
                    data={
                          'pm_id': object_pm.id,
                          'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                          'km_interval': object_pm.km_interval,
                          'km_last_done': object_pm.km_last_done,
                          'km_warn_period': object_pm.km_warn_period,
                          'state_process': 'progress',
                          }
                elif object_pm.meter == 'days':
                    data={
                          'pm_id': object_pm.id,
                          'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                          'days_interval': object_pm.days_interval,
                          'days_last_done': object_pm.days_last_done,
                          'days_warn_period': object_pm.days_warn_period,
                          'state_process': 'progress',
                          }
                self.pool.get('tms.gmao.pm.alert').create(cr, uid, data, {'alert_ok': True})
                self.write(cr, uid, ids, {'draft_ok':False})
            return True

    def _get_info_alert_view(self, cr, uid, ids, prop, unknow_none, context):
        u"""Récupération des données (km/jours) de l'alerte"""
        data = {}
        if ids:
            for object_pm in self.browse(cr, uid, ids, context):
                data[object_pm.id]={
                                       'interval_view' : '',
                                        'last_done_view' : '',
                                        'next_due_view' : '',
                                        'warn_period_view' : '',
                                        'left_view' : '',
                                       }
                if object_pm.meter=='km':
                    data[object_pm.id]['interval_view'] = u'%d km' %(object_pm.km_interval or 0)
                    data[object_pm.id]['last_done_view'] = u'%d km' %(object_pm.km_last_done or 0)
                    data[object_pm.id]['next_due_view'] = u'%d km' %(object_pm.km_next_due or 0)
                    data[object_pm.id]['warn_period_view'] = u'%d km' %(object_pm.km_warn_period or 0)
                    data[object_pm.id]['left_view'] = u'%d km' %(object_pm.km_left or 0)
                elif object_pm.meter=='days':
                    data[object_pm.id]['interval_view'] = u'%d jours' %(object_pm.days_interval or 0)
                    data[object_pm.id]['last_done_view'] = u'%s' %(object_pm.days_last_done or u'Non défini')
                    data[object_pm.id]['next_due_view'] = u'%s' %(object_pm.days_next_due or u'Non défini')
                    data[object_pm.id]['warn_period_view'] = u'%d jours' %(object_pm.days_warn_period or 0)
                    data[object_pm.id]['left_view'] = u'%d jours' %(object_pm.days_left or 0)
        return data

    def _get_pm_change(self, cr, uid, ids, context={}):
        result = {}
        ids_pm=self.pool.get('tms.gmao.pm').search(cr, uid, [])
        for id_pm in ids_pm:
            result[id_pm] = True
        return result.keys()

    def log_validate_alert(self,cr,uid,id_alert,context={}):
        u"""Journalisation de la validation alerte"""
        pass

    _columns = {
        'name': fields.char(u'Réf MP', size=20),
        'vehicle_id': fields.many2one('fleet.vehicle', u'Véhicule/SR'),
        #'trailer': fields.many2one('tms.truck.trailer', u'Semi-remorque', required=False),
        #'tyre': fields.many2one('tms.gmao.tyre', u'Pneu', required=False,),
        #'vehicle_assigned' : fields.many2one('tms.truck.vehicle',u'Véhicule assigné au pneu',readonly=True),
        #'trailer_assigned' : fields.many2one('tms.truck.trailer',u'Semi-remorque assigné au pneu',readonly=True),
        #'type_assigned' : fields.selection([('vehicle',u'Véhicule'),('trailer',u'Semi-remorque')],u'type assigné',readonly=False),
        'type_alert': fields.function(_get_type_alert, method=True, type="char", string=u'Type alerte', store=True),
        #'type' : fields.selection([('vehicle',u'Véhicule'),('trailer',u'Semi-remorque'),('tyre',u'Pneu')],'type',readonly=False,required=True),
        'description': fields.text(u'Description'),
        #'type_maintainance_vehicle':fields.selection([
        #                ('technical_round',u'visite technique'),
        #                ('sewage',u'Vidange'),
        #                ('spare',u'Affectation pièce détachée'),
        #                ('control',u'Controle general'),
        #                          ],u'Type MP',),
        #'type_maintainance_trailer':fields.selection([
        #                ('technical_round',u'visite technique'),
        #                ('sewage',u'Vidange'),
        #                ('spare',u'Affectation pièce détachée'),
        #                ('control',u'Controle general'),
        #                          ],u'Type MP',),
        #'type_maintainance_tyre':fields.selection([
        #                ('unmount',u'Démontage pneu'),
        #                          ],u'Type MP',),
        'service_type_id': fields.many2one('fleet.service.type', string=u"Type d'intervention", domain=[('mro_ok','=',True)]),
        'meter': fields.selection([('days', u'Jours'),('km', u'Km')], u'Unité de mesure', required=True),
        #'typemesure': fields.selection([
        #                ('jour', u'Jour'),
        #                ('Hebdomadaire', u'Hebdomadaire'),
        #                ('quinzaine', u'Quinzaine'),
        #                ('mensuel', u'Mensuel'),
        #                ('trimestriel', u'Trimestriel'),
        #                ('semestriel', u'Semestriel'),
        #                ('annuel', u'Annuel'),
        #                          ], u'Unités de mesure'),
        'periodic': fields.boolean(u'Périodique ?', help=u"Cochez cette option si la maintenance programmée est periodique."),
        #'category': fields.many2one('tms.gmao.pm.category', u'Catégorie'),
        'days_interval': fields.integer(u'Intervalle', help=u"Le nombre de jours avant la prochaine maintenance."),
        'days_last_done': fields.date(u'Commencer le', required=True),
        'days_next_due': fields.function(_get_information_alert, method=True, type="date", string=u'Prochaine date', multi="sums"),
        'days_warn_period': fields.integer(u'Date alerte'),
        'days_left': fields.function(_get_information_alert, method=True, type="integer", string=u'Jours restant', multi="sums"),
        'km_interval': fields.float(u'Intervalle', help=u"Le nombre de kilomètres avant la prochaine maintenance."),
        'km_last_done': fields.float(u'Commencer à',required=True),
        'km_next_due': fields.function(_get_information_alert, method=True, type="integer", string=u'Prochain km', multi="sums"),
        'km_warn_period':fields.float('Km alerte'),
        'km_left': fields.function(_get_information_alert, method=True, type="integer", string=u'Km restant', multi="sums"),
        'interval_view': fields.function(_get_info_alert_view, method=True, type='char', string=u'Intervalle', multi="view"),
        'last_done_view' : fields.function(_get_info_alert_view, method=True, type='char', string=u'Commence', multi="view"),
        'next_due_view' : fields.function(_get_info_alert_view, method=True, type='char', string=u'Termine', multi="view"),
        'warn_period_view' : fields.function(_get_info_alert_view, method=True, type='char', string=u'Alerte dans', multi="view"),
        'left_view' : fields.function(_get_info_alert_view, method=True, type='char', string=u'Restant', multi="view"),
        'counter_current': fields.float(u"Kilométrage actuel", readonly=True),
        'draft_ok' : fields.boolean(u'Brouillon de création'),
        'state': fields.function(_get_information_alert, method=True, type="selection",selection=[('draft', u'Normal'),
                                    ('left', u'Dépassé'),
                                    ('alert', u'Alerte'),
                                    ('done', u'Terminé')], string='Statut', multi="sums", store={
                                    'fleet.vehicle': (_get_pm_change, None, 20),
                                    #'tms.truck.trailer': (_get_pm_change, None, 20),
                                    'tms.gmao.pm': (_get_pm_change, [], 20),
                                    'tms.gmao.pm.alert': (_get_pm_change, [], 25),
                                    'tms.picking': (_get_pm_change, [], 20),
                                    },),
        'alert_ids': fields.one2many('tms.gmao.pm.alert', 'pm_id', u'Suivi des alertes'),
        }

    _defaults = {
        'meter': lambda * a: 'days',
        #'typemesure': lambda * a:'jour',
        'periodic': lambda * a: True,
        'days_last_done': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'name' : lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'tms.gmao.pm'),
        #'type': lambda *a: 'vehicle',
        #'type_maintainance_vehicle':lambda *a: 'technical_round',
        #'type_maintainance_trailer':lambda *a: 'sewage',
        #'type_maintainance_tyre':lambda *a: 'unmount',
        #'typemesure' : lambda *a : 'jour',
        'draft_ok': lambda *a: True,
        }

    #def onchange_tyre(self,cr,uid,ids,tyre=False,type_maintainance_tyre=False,context={}):

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id, context={}):
        u"""Évènement lors du changement du véhicule"""
        data={'km_last_done': 0.0}
        if vehicle_id:
            object_vehicle=self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context)
            if object_vehicle:
                if object_vehicle.vehicle_ok:
                    if self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_current_counter'], context)['tms_gmao_param_current_counter'] == False:
                        data['km_last_done'] =  object_vehicle.fuel_odometer
                    else:
                        data['km_last_done'] = object_vehicle.odometer
                else:
                    data['km_last_done'] = object_vehicle.odometer
        return {'value': data}

tms_gmao_pm()

class tms_gmao_pm_alert(osv.osv):
    u"""Alertes"""
    _name = "tms.gmao.pm.alert"
    _description = u"Suivi des alertes maintenance périodiques"
    _order = "date desc"

    def create(self, cr, user, vals, context=None):
        u"""Méthode de création"""
        if context:
            flag_alert = context.get('alert_ok', False)
            if flag_alert:
                id_alert = super(tms_gmao_pm_alert, self).create(cr, user, vals, context)
                return id_alert
            else:
                raise osv.except_osv(u'Mauvaise procédure!', u'Pour créer une alerte, veuillez créer une maintenance programmée.')
        else:
            raise osv.except_osv(u'Mauvaise procédure!', u'Pour créer une alerte, veuillez créer une maintenance programmée.')

    def unlink(self, cr, uid, ids, context=None):
        u"""Méthode de suppression"""
        raise osv.except_osv(u'Suppression impossible', u'Vous ne pouvez pas supprimer une alerte, songez à l\'annuler.')
        return super(tms_gmao_pm_alert, self).unlink(cr, uid, ids, context)   
    
    def copy(self, cr, uid, id, default=None, context={}):
        u"""Méthode de copie"""
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tms.gmao.pm.alert')
        default['maintenance_ids']=[]
        #default['maintenance_group_ids']=[]
        default['state'] = 'draft'
        return super(tms_gmao_pm_alert, self).copy(cr, uid, id, default, context)     
    
    def _value_next_due(self, cr, uid, ids, prop, unknow_none, context):
        u"""Calcul des prochaines données d'alerte"""
        if ids:
            reads = self.browse(cr, uid, ids, context)
            res = {}
            for record in reads:
                res[record.id]={
                                'days_next_due' : False,
                                'km_next_due' : 0,
                                }
                if (record.meter == "days"):
                    interval = datetime.timedelta(days=record.days_interval)
                    last_done = record.days_last_done
                    last_done = datetime.datetime.fromtimestamp(time.mktime(time.strptime(last_done, "%Y-%m-%d")))
                    next_due = last_done + interval
                    res[record.id]['days_next_due']= next_due.strftime("%Y-%m-%d")
                elif (record.meter == "km"):
                    km_next_due=record.km_last_done + record.km_interval
                    res[record.id]['km_next_due']= km_next_due
        return res

    def _value_due(self, cr, uid, ids, prop, unknow_none, context):
        u"""Calcul du temps/km restant"""
        if ids:
            reads = self.browse(cr, uid, ids, context)
            res = {}
            for record in reads:
                res[record.id]={
                            'days_left' : 0,
                            'km_left' : 0,          
                            }
                if record.state_process == 'progress':
                    if (record.meter == "days"):
                        interval = datetime.timedelta(days=record.days_interval)
                        last_done = record.days_last_done
                        last_done = datetime.datetime.fromtimestamp(time.mktime(time.strptime(last_done, "%Y-%m-%d")))
                        next_due = last_done + interval
                        NOW = datetime.datetime.now()
                        due_days = next_due - NOW
                        res[record.id]['days_left']= due_days.days
                    elif (record.pm_id):
                        if (record.pm_id.meter == "km"):
                            current_km=0
                            if record.vehicle_id:
                                if record.vehicle_id.vehicle_ok:
                                    if self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_current_counter'], context)['tms_gmao_param_current_counter'] == False:
                                        current_km =  record.vehicle_id.fuel_odometer
                                    else:
                                        current_km = record.vehicle_id.odometer
                                else:
                                    current_km = record.vehicle_id.odometer
                            res[record.id]['km_left']= record.km_next_due - current_km
            return res
    
    def action_done_alert(self, cr, uid, ids, context=None):
        u"""Valider l'alerte"""
        object_pm_alert = self.browse(cr, uid, ids[0], context)
        
        if context is None: context = {}
        context = dict(context, active_ids=ids, active_model=self._name)
        if not (ids or object_pm_alert.vehicle_id):
            return False
        if object_pm_alert.vehicle_id.vehicle_ok:
            alert_process_id=False
            alert_name=''
            alert_res_model=''
            alert_view_id=False
            km=0
            if self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_current_counter'], context)['tms_gmao_param_current_counter'] == False:
                km =  object_pm_alert.vehicle_id.fuel_odometer
            else:
                km = object_pm_alert.vehicle_id.odometer
            data_alert_process = {
                'vehicle_id': object_pm_alert.vehicle_id and object_pm_alert.vehicle_id.id or False,
                #'type' : 'vehicle',
                'periodic_ok': object_pm_alert.periodic,
                'alert_id': object_pm_alert.id,    
                'km': km,
                'meter': object_pm_alert.meter,
                'description':object_pm_alert.description,   

                }
            alert_process_id = self.pool.get("tms.gmao.pm.alert.process").create(cr, uid, data_alert_process, context=context)
            alert_view_id = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','tms.gmao.pm.alert.process'),('name','=','tms.gmao.pm.alert.process.form')])
            alert_name=u'Assistant Ordre de maintenance'
            alert_res_model='tms.gmao.pm.alert.process'
            if alert_process_id:
                return {
                    'name': alert_name,
                    'view_mode': 'form',
                    'view_id': alert_view_id,
                    'view_type': 'form',
                    'res_model': alert_res_model,
                    'res_id': alert_process_id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                    'context': context,
                    }
        elif object_pm_alert.vehicle_id.trailer_ok:
            alert_process_id=False
            alert_name=''
            alert_res_model=''
            alert_view_id=False
            data_alert_process={
                'vehicle_id': object_pm_alert.vehicle_id and object_pm_alert.vehicle_id.id or False,
                #'type' : 'trailer',
                'periodic_ok': object_pm_alert.periodic,
                'alert_id': object_pm_alert.id or False,   
                'km': object_pm_alert.vehicle_id.odometer,
                'meter': object_pm_alert.meter,  
                'description':object_pm_alert.description,   
                }
            alert_process_id = self.pool.get("tms.gmao.pm.alert.process").create(cr, uid, data_alert_process, context=context)
            alert_view_id = self.pool.get('ir.ui.view').search(cr,uid,[('model','=','tms.gmao.pm.alert.process'),('name','=','tms.gmao.pm.alert.process')])
            alert_name = u'Assistant Ordre de maintenance'
            alert_res_model = 'tms.gmao.pm.alert.process'
            if alert_process_id:
                return {
                                'name': alert_name,
                                'view_mode': 'form',
                                'view_id': alert_view_id,
                                'view_type': 'form',
                                'res_model': alert_res_model,
                                'res_id': alert_process_id,
                                'type': 'ir.actions.act_window',
                                'nodestroy': True,
                                'target': 'new',
                                'domain': '[]',
                                'context': context,
                            }
            #elif object_pm_alert.type == 'tyre': #@TODO xhexk how to manage tyre mro
        return True
    
    def action_cancel_alert(self,cr,uid,ids,context={}):
        u"""Annuler l'alerte"""
        if ids:
            for object_alert in self.browse(cr,uid,ids):
                if object_alert.state_process == 'progress':
                    ids_search_mro_orders = self.pool.get('mro.order').search(cr,uid,[('alert_id','=',object_alert.id),('state','=','done')])
                    if ids_search_mro_orders:
                        self.pool.get('mro.order').action_cancel(cr, uid, ids_search_mro_orders)
                    self.write(cr,uid,object_alert.id,{'state_process':'cancel',})
        return True
                        
    def validate_alert(self,cr,uid,id_alert,periodic=True,date=False,km=False,context={}):
        u"""valider l'alerte"""
        if id_alert:
            object_alert = self.browse(cr,uid,id_alert)
            if object_alert:
                data_write={
                            'state_process' : 'done',
                            }
                res_write_alert=self.pool.get('tms.gmao.pm.alert').write(cr,uid,[id_alert],data_write)
                if res_write_alert:
                    object_alert=self.browse(cr,uid,id_alert)
                    if object_alert:
                        self.pool.get('tms.gmao.pm').log_validate_alert(cr, uid, object_alert.id)
                #create new alert
                if object_alert.pm_id:
                    if object_alert.periodic == True:
                        if periodic==False:
                            self.pool.get('tms.gmao.pm').write(cr,uid,[object_alert.pm_id.id],{'periodic' :False})
                        elif periodic:
                            if object_alert.meter == 'km':
                                km_last_done= object_alert.km_next_due
                                if km!=False :
                                    km_last_done=km
                                else:
                                    if object_alert.vehicle_id.vehicle_ok:
                                        if self.pool.get('tms.gmao.config.settings').default_get(cr, uid, ['tms_gmao_param_current_counter'], context)['tms_gmao_param_current_counter'] == False:
                                            km_last_done = object_alert.vehicle_id and object_alert.vehicle_id.fuel_odometer or 0
                                        else:
                                            km_last_done = object_alert.vehicle_id and object_alert.vehicle_id.odometer or 0
                                    elif object_alert.vehicle_id.trailer_ok:
                                        km_last_done=object_alert.vehicle_id and object_alert.vehicle_id.odometer or 0
                                data={
                                      'pm_id' : object_alert.pm_id and object_alert.pm_id.id or False,
                                      'date' : date,
                                      'km_interval' : object_alert.km_interval,
                                      'km_last_done' : km_last_done,
                                      'km_warn_period' : object_alert.km_warn_period,
                                      'state_process' : 'progress',
                                      }
                            elif object_alert.meter == 'days':
                                if not date:
                                    date=time.strftime('%Y-%m-%d %H:%M:%S'),
                                data={
                                      'pm_id' : object_alert.pm_id and object_alert.pm_id.id or False,
                                      'date' :  time.strftime('%Y-%m-%d %H:%M:%S'),
                                      'days_interval' : object_alert.days_interval,
                                      'days_last_done' : date,
                                      'days_warn_period' : object_alert.days_warn_period,
                                      'state_process' : 'progress',
                                      }
                            id_alert=self.pool.get('tms.gmao.pm.alert').create(cr,uid,data,{'alert_ok' : True})
                    else:
                        self.pool.get('tms.gmao.pm').write(cr,uid,[object_alert.pm_id.id],{'periodic' : False})
        return True

    def _get_state(self, cr, uid, ids, prop, unknow_none, context):
        u"""récupérer l'état"""
        res = {}
        if ids:
            reads = self.browse(cr, uid, ids, context)
            for record in reads:  
                res[record.id] = 'done'
                if record.state_process == 'progress':            
                    if record.meter == 'days':
                        if (record.days_left <= 0):
                            res[record.id] = 'left'
                        elif (record.days_left <= record.days_warn_period):
                            res[record.id] = 'alert'
                        else:
                            res[record.id] = 'draft'
                    elif record.meter == 'km':
                        if (record.km_left <= 0):
                            res[record.id] = 'left'
                        elif (record.km_left <= record.km_warn_period):
                            res[record.id] = 'alert'
                        else:
                            res[record.id] = 'draft'
        return res
    
    def _get_type_alert(self, cr, uid, ids, prop, unknow_none, context):
        u"""récupérer le type d'alerte"""
        res = {}
        if ids:
            reads = self.browse(cr, uid, ids, context)
            for record in reads:  
                res[record.id] = record.pm_id and record.pm_id.type_alert or ''
                #if record.pm_id:
                #    if record.pm_id.type:
                #        if record.pm_id.type=='vehicle':
                #            res[record.id] = type_maintainance_vehicle[record.pm_id.type_maintainance_vehicle]
                #        elif record.pm_id.type=='trailer':
                #            res[record.id] = type_maintainance_trailer[record.pm_id.type_maintainance_trailer]
                #        elif record.pm_id.type=='tyre':
                #            res[record.id] = type_maintainance_tyre[record.pm_id.type_maintainance_tyre]
        return res
    
    def _get_info_alert_view(self, cr, uid, ids, prop, unknow_none, context):
        u"""récupérer les infos d'alerte"""
        data = {}
        if ids:
            for object_alert in self.browse(cr, uid, ids, context):
                data[object_alert.id]={
                                       'interval_view' : '',
                                        'last_done_view' : '',
                                        'next_due_view' : '',
                                        'warn_period_view' : '',
                                        'left_view' : '',
                                       }
                if object_alert.pm_id:
                    if object_alert.pm_id.meter=='km':
                        data[object_alert.id]['interval_view'] = u'%d km' %(object_alert.km_interval or 0)
                        data[object_alert.id]['last_done_view'] = u'%d km' %(object_alert.km_last_done or 0)
                        data[object_alert.id]['next_due_view'] = u'%d km' %(object_alert.km_next_due or 0)
                        data[object_alert.id]['warn_period_view'] = u'%d km' %(object_alert.km_warn_period or 0)
                        data[object_alert.id]['left_view'] = u'%d km' %(object_alert.km_left or 0)
                    elif object_alert.pm_id.meter=='days':
                        data[object_alert.id]['interval_view'] = u'%d jours' %(object_alert.days_interval or 0)
                        data[object_alert.id]['last_done_view'] = u'%s' %object_alert.days_last_done
                        data[object_alert.id]['next_due_view'] = u'%s' %object_alert.days_next_due
                        data[object_alert.id]['warn_period_view'] = u'%d jours' %(object_alert.days_warn_period or 0)
                        data[object_alert.id]['left_view'] = u'%d jours' %(object_alert.days_left  or 0)
        return data
    
    def _get_pm_alert_change(self,cr,uid,ids,context={}):
        result = {}
        ids_pm_alert=self.pool.get('tms.gmao.pm.alert').search(cr,uid, [])
        for id_pm_alert in ids_pm_alert:
            result[id_pm_alert] = True
        return result.keys()

    _columns = {
        'name': fields.char(u'Alerte', size=32,readonly=True),
        'date': fields.datetime(u'Date',readonly=True),
        'description': fields.text(u'Description'),
        'pm_id': fields.many2one('tms.gmao.pm', u'Maint. Prog.', required=True, readonly=True),
        'meter': fields.related('pm_id', 'meter', type='selection', selection=[('days', u'Jours'),('km', u'Km')], string=u'Unité de mesure', store=True),
        'vehicle_id': fields.related('pm_id', 'vehicle_id', type='many2one', string=u'Véhicule', relation="fleet.vehicle", readonly=True, store=True),
        #'trailer' : fields.related('pm_id','trailer',type='many2one',string=u'Semi-remorque',relation="tms.truck.trailer",readonly=True,store=True),
        #'tyre' : fields.related('pm_id','tyre',type='many2one',string=u'Pneu',relation="tms.gmao.tyre",readonly=True,store=True),
        #'type' : fields.related('pm_id','type',type='selection',selection=[('vehicle',u'Véhicule'),('trailer',u'Semi-remorque'),('tyre',u'Pneu')],string=u'Type',readonly=True,store=True),
        'periodic': fields.related('pm_id', 'periodic', type='boolean', string=u'Périodique', readonly=True, store=True),
        #'category' : fields.related('pm_id','category',type='many2one',relation='tms.gmao.pm.category',string=u'Catégorie',store=True,readonly=True),
        #'type_maintainance_vehicle':fields.related('pm_id','type_maintainance_vehicle',type='selection',selection=[('technical_round',u'visite technique'),
        #                ('sewage',u'Vidange'),
        #                ('spare',u'Affectation pièce détachée'),
        #                ('control',u'Controle general'),],string=u'Type maintenance véhicule',readonly=True,store=True),
        #'type_maintainance_trailer':fields.related('pm_id','type_maintainance_trailer',type='selection',selection=[('sewage',u'Vidange'),
        #                ('spare',u'Affectation pièce détachée'),
        #                ('control',u'Controle general'),],string=u'Type maintenance semi-remorque',store=True),
        #'type_maintainance_tyre':fields.related('pm_id','type_maintainance_tyre',type='selection',selection=[('unmount',u'Démontage pneu'),],string=u'Type maintenance pneu',store=True),
        #'maintenance_group_ids' : fields.one2many('tms.gmao.maintenance.group','alert_id',u'Groupe de maintenances',readonly=True),
        'maintenance_ids': fields.one2many('mro.order', 'alert_id', u'Maintenances', readonly=True),
        'type_alert': fields.function(_get_type_alert, method=True, type="char", string=u'Type alerte', store=True),
        'days_interval': fields.integer(u'Intervalle', help=u"Le nombre de jours avant la prochaine maintenance."),
        'days_last_done': fields.date(u'Commencer le',),
        'days_next_due': fields.function(_value_next_due, method=True, type="date", string=u'Prochaine date', multi='sums'),
        'days_warn_period': fields.integer(u'Date alerte'),
        'days_left': fields.function(_value_due, method=True, type="integer", string=u'Jours restant', multi='meta'),
        'km_interval': fields.integer(u'Intervalle', help=u"Le nombre de kilomètres avant la prochaine maintenance."),
        'km_last_done': fields.integer(u'Commencer à',),
        'km_next_due': fields.function(_value_next_due, method=True, type="integer", string=u'Prochain km', multi='sums'),
        'km_warn_period': fields.integer(u'Km alerte'),
        'km_left': fields.function(_value_due, method=True, type="integer", string=u'Km restant',multi='meta'),
        'state_process' : fields.selection(
                                   [('progress', u'En cours'),
                                    ('done', u'Traité'),
                                    ('cancel', u'Annulé'),
                                    ], u'traitement', required=True, readonly=True,
                                   ),
        'interval_view': fields.function(_get_info_alert_view,method=True,type='char',string=u'Intervalle',multi="view"),
        'last_done_view': fields.function(_get_info_alert_view,method=True,type='char',string=u'Commence',multi="view"),
        'next_due_view': fields.function(_get_info_alert_view,method=True,type='char',string=u'Fini',multi="view"),
        'warn_period_view': fields.function(_get_info_alert_view,method=True,type='char',string=u'alerte',multi="view"),
        'left_view': fields.function(_get_info_alert_view,method=True,type='char',string=u'Restant',multi="view"),
        'state': fields.function(_get_state, method=True, type="selection", selection=[('draft',u'Normal'),
                                    ('left', u'Dépassé'),
                                    ('alert', u'Alerte'),
                                    ('done', u'Validé')], string=u'Etat', store={
                                    'fleet.vehicle': (_get_pm_alert_change, None, 20),
                                    #'tms.truck.trailer': (_get_pm_alert_change, None, 20),
                                    'tms.gmao.pm': (_get_pm_alert_change, [], 25),
                                    'tms.gmao.pm.alert': (_get_pm_alert_change, [], 20),
                                    'tms.picking': (_get_pm_alert_change, [], 20),
                                    },),
    }
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'days_last_done': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'km_last_done': lambda *a: 0, 
        'km_warn_period': lambda *a: 0,  
        'state_process' : lambda *a: 'progress',
        'name': lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z, 'tms.gmao.pm.alert'),
        }

tms_gmao_pm_alert()
