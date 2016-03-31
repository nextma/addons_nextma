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
from openerp.osv import osv,fields
import time

class hr_employee_licence_category(osv.osv):
    _name="hr.employee.licence_category"
    _columns={
            'name' : fields.char('Catégorie de permis'),
        }

class hr_employee(osv.osv):
    _name="hr.employee"
    _inherit="hr.employee"

    
    def unlink(self, cr, uid, ids, context=None):
        u"""Méthode de suppression"""
        self.write(cr,uid,ids,{'active' : False})
        return True 
    
    def _get_travel_ids(self, cr, uid, ids, name, args, context=None):
        u"""Récupère les voyages effectués par le chauffeur"""
        data = {}
        for object_hr_employee in self.browse(cr,uid,ids,context):
            data[object_hr_employee.id]={
                                          'effective_travels':[],
                                          'travels_qty' : 0,
                                          }
            search_args = [('driver_id','=',object_hr_employee.id)]
            data_search_id_travels = self.pool.get('tms.travel').search(cr,uid,search_args)
            data[object_hr_employee.id]['effective_travels'].extend(data_search_id_travels)
            data[object_hr_employee.id]['travels_qty'] = len(data_search_id_travels)
        return data

    def get_travel_disponibility(self, cr, uid, picking_id, driver_id, date, date_end): 
        u"""Disponibilité du chauffeur pour le voyage"""
        cr.execute(
                       """
                       SELECT id, name AS name FROM tms_picking 
                       WHERE id != %s
                       AND ((date >= '%s' and date<= '%s') OR (date_end >= '%s' and date_end <= '%s'))
                       AND driver_id = %d
                       AND state NOT IN ('draft', 'cancel')
                       ORDER BY
                       DATE desc
                       """%(picking_id, date, date_end, date, date_end, driver_id)
                       )

        for item in cr.dictfetchall():
            return [False, item['name']]
        return [True]

    def _get_actual_disponibility(self, cr, uid, ids, name, args, context=None): 
        u"""Disponibilité actuelle du chauffeur"""
        data={}
        my_date = time.strftime('%Y-%m-%d %H:%M:%S')
        my_date_start = time.strftime('%Y-%m-%d 00:00:00')
        my_date_end = time.strftime('%Y-%m-%d 23:59:59')
        for driver in self.browse(cr, uid, ids, context=context):
            data[driver.id] = {
                                'disponibility': 'available',
                                'current_travel': u'Pas de voyage',
                                'current_date_travel': False,
                               }
            #if self.pool.get('tms.param').get_value_by_reference(cr,uid,'tms','tms_param_include_tax') == True: @TODO try to understand it !
            cr.execute(
                       """
                       select id, name, date from tms_picking 
                       where date >= '%s' and date<= '%s'
                        and driver_id = %d
                        and state != 'cancel'
                        order by
                        date desc
                       """%(my_date_start, my_date_end, driver.id)
                       )

            for item in cr.dictfetchall():
                data[driver.id]['current_travel'] = u'%s' %(item['name'])
                data[driver.id]['current_date_travel'] = item['date']
                data[driver.id]['disponibility'] = 'unavailable'
                break
        return data 

    _columns = {
        'driver_ok':fields.boolean(u'Chauffeur', help=u"Cochez cette case pour définir l'employé comme chauffeur pour la gestion de voyages"),
        'attendant_ok' : fields.boolean(u'Pompiste', help=u"Cochez cette case pour définir l'employé comme pompiste pour la gestion de bons carburants"),
        'license_no':fields.char(u'Numéro permis', size=25, help=u"Numéro de permis"),
        'date_of_expiry':fields.date(u'Date Expiration Permis', required=False),
        #'contract':fields.char(_(u'Contrat'),size=25),
        #'post':fields.char(_(u'Poste'),size=25),
        'date_delivery_car_licence': fields.date(u'Date Délivrance'),
        'car_licence_category':fields.many2many('hr.employee.licence_category','employee_licence_category_rel','employee_id','licence_category_id',string='Catégorie Permis'),
        'point_driving': fields.integer(u'Nombre de points', help=u"Nombre de points du permis"),
        'date_hiring': fields.date(u'Date d\'embauche'),
        'accident_qty': fields.integer(u'Nombre d\'accidents', help=u"Nombre d'accidents occasionnés durant son activité"),
        #'travels_qty': fields.function(_get_travel_ids, method=True, type='integer',string=u'Nombre de voyages', multi='sums'),
        'vehicle_id' : fields.many2one('fleet.vehicle', u'Véhicule affecté'),
        #'effective_travels' : fields.function(_get_travel_ids, method=True, type='one2many', obj='tms.travel', string=u'Voyages effectués', multi='sums'),
        'disponibility': fields.function(_get_actual_disponibility, method=True, type='selection', string=u'statut-voyage', multi='current_travel', 
                        selection=[('available', u'Disponible'),('unavailable', u'En voyage')]),
        'current_travel': fields.function(_get_actual_disponibility, method=True, type='char', string=u'Voyage en cours', multi='current_travel'),
        'current_date_travel' : fields.function(_get_actual_disponibility,method=True,type='datetime',string=u'date voyage',multi='current_travel'),
        }
    
    _defaults={
        'driver_ok':lambda *a: False,
        'attendant_ok' : lambda *a : False,
        }
    _sql_constraints = [
        ('date_employee_check', "CHECK ( date_hiring <= date_of_expiry )", "La date d'expiration du permis doit être supérieure à celle d'embauche"),
        ('accident_qty_check', "CHECK ( 0 <= accident_qty )", "Le nombre d'acident doit être une valeur positive"),
    ]
hr_employee()
