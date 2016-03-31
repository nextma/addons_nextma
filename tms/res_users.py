# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
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
#from functools import partial
#import logging
#from lxml import etree
#from lxml.builder import E

#import openerp
#from openerp import SUPERUSER_ID
#from openerp import pooler, tools
#import openerp.exceptions
from openerp.osv import fields,osv
#from openerp.osv.orm import browse_record
from openerp.tools.translate import _

__author__ = "NEXTMA"
__version__ = "0.1"
#__date__ = u"22 Décembre 2013"

class res_users(osv.osv):
    _name = "res.users"
    _inherit = 'res.users'

    def _default_parks(self, cr, uid, context=None):
        u"""Récupère le parc par défaut"""
        data=[]
        ids_search=self.pool.get('ir.model.data').search(cr,uid,[('name','=','tms_park_all')])
        if ids_search:
            object_data=self.pool.get('ir.model.data').browse(cr,uid,ids_search[0])
            if object_data:
                return object_data.res_id
        return data
    
    _columns = {
        'park_id': fields.many2one('fleet.park', u'Parc par défaut', required=True, help=u"Sélectionnez le parc adéquat pour l'utilisateur, vous pouvez segmenter vos parcs et les assigner aux utilisateurs correspondants."),
        }

    _defaults = {  
        'park_id': _default_parks,
        #'menu_tips' : lambda *a: True,
        }
    
    def get_list_vehicle_id(self,cr,uid):
        u"""Récupère la liste des véhicules disponibles pour l'utilisateur"""
        data=[]
        if uid:
            object_user=self.browse(cr,uid,uid)
            if object_user:
                if object_user.park_id: 
                    object_park=self.pool.get('fleet.park').browse(cr,uid,object_user.park_id.id)
                    if object_park:
                        if object_park.all_vehicle_ok == False:
                            data.extend([object_vehicle.id for object_vehicle in object_park.vehicle_ids])
        return data
    
    def get_all_vehicle_ok(self,cr,uid):
        u"""Récupère la liste de tous les véhicules l'utilisateur"""
        result=True
        if uid:
            object_user=self.browse(cr,uid,uid)
            if object_user:
                if object_user.park_id:
                    object_park=self.pool.get('fleet.park').browse(cr,uid,object_user.park_id.id)
                    if object_park:
                        if object_park.all_vehicle_ok == False:
                            return False
        return result

    def get_list_traject_id(self,cr,uid):
        u"""Récupère la liste des trajets disponibles pour l'utilisateur"""
        data=[]
        if uid:
            object_user=self.browse(cr,uid,uid)
            if object_user:
                if object_user.park_id:
                    object_park=self.pool.get('fleet.park').browse(cr,uid,object_user.park_id.id)
                    if object_park:
                        if object_park.all_traject_ok == False:
                            data.extend([object_traject.id for object_traject in object_park.traject_ids])
        return data
    
    def get_all_traject_ok(self,cr,uid):
        u"""Récupère la liste de tous les trajets disponibles pour l'utilisateur"""
        result=True
        if uid:
            object_user=self.browse(cr,uid,uid)
            if object_user:
                if object_user.park_id:
                    object_park=self.pool.get('fleet.park').browse(cr,uid,object_user.park_id.id)
                    if object_park:
                        if object_park.all_traject_ok == False:
                            return False
        return result

    def get_list_partner_id(self,cr,uid):
        u"""Récupère la liste des clients disponibles pour l'utilisateur"""
        data=[]
        if uid:
            object_user=self.browse(cr,uid,uid)
            if object_user:
                if object_user.park_id:
                    object_park=self.pool.get('fleet.park').browse(cr,uid,object_user.park_id.id)
                    if object_park:
                        if object_park.all_partner_ok == False:
                            data.extend([object_partner.id for object_partner in object_park.partner_ids])
        return data
    
    def get_all_partner_ok(self,cr,uid):
        u"""Récupère la liste de tous les clients pour l'utilisateur"""
        result=True
        if uid:
            object_user=self.browse(cr,uid,uid)
            if object_user:
                if object_user.park_id:
                    object_park=self.pool.get('fleet.park').browse(cr,uid,object_user.park_id.id)
                    if object_park:
                        if object_park.all_partner_ok == False:
                            return False
        return result
    
res_users()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
