# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
import pydoc

class tms_gmao_pm_alert_process(osv.osv_memory):
    u"""Traitement alerte"""
    _name = "tms.gmao.pm.alert.process"
    _description = u"Traitement alerte"

    def _default_user(self, cr, uid, context=None):
        u"""utilisateur par défaut"""
        return uid

    _columns = {
            #'order_id': fields.many2one('mro.order', u'Ordre de maintenance'),
            'alert_id': fields.many2one('tms.gmao.pm.alert',u'alerte',required=True,readonly=True),
            'vehicle_id': fields.many2one('fleet.vehicle', u'Véhicule', readonly=True),
            'periodic_done': fields.boolean(u'Terminer la périodicité de la maintenance'),
            'date': fields.datetime(u'Date', required=True),
            'maintenancier_id': fields.many2one('hr.employee',u'Maintenancier'),
            'line_ids': fields.one2many('tms.gmao.pm.alert.process.line','process_id', u'Vidanges'),
            'periodic_ok': fields.boolean(u'Périodique'),
            'meter': fields.selection([ ('days', u'Jours'),('km', u'km')], u'Unité de mesure',required=True),
            'km': fields.float('KM'),
            'description': fields.char(u'Description', size=50, required=True),
            'user_id': fields.many2one('res.users', u'Responsable'),
            }
    _defaults = {
        'user_id' : _default_user,
        'periodic_done': lambda *a: False,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'km': lambda *a : 0,
        }
    
    def action_done(self,cr,uid,ids,context={}):
        u"""Effectuer maintenance"""
        for object_process in self.browse(cr, uid, ids):
            if object_process.line_ids:
                mro_datas={
                       'maintenance_type': 'pm',
                       'service_type_id': object_process.alert_id and object_process.alert_id.pm_id and object_process.alert_id.pm_id.service_type_id.id or False,
                       'origin': object_process.alert_id and object_process.alert_id.pm_id and object_process.alert_id.pm_id.name or "",
                       'user_id' : object_process.user_id and object_process.user_id.id or False,
                       'vehicle_id': object_process.vehicle_id and object_process.vehicle_id.id or False,
                       'description': object_process.description,
                       'date_planned': object_process.date,
                       'date_scheduled': object_process.date,
                       'date_execution': object_process.date,
                       #'triggering': 'alert',
                       'alert_id': object_process.alert_id and object_process.alert_id.id or False,
                       'km_start': object_process.km or 0,
                       'maintenancier_id' : object_process.maintenancier_id and object_process.maintenancier_id.id or False,
                       }
                mro_id = self.pool.get('mro.order').create(cr, uid, mro_datas)
                if mro_id:
                    for object_process_line in object_process.line_ids:
                        parts_datas = {
                            'name' : object_process_line.description,
                            'parts_id' : object_process_line.product_id and object_process_line.product_id.id or False,
                            'parts_uom' : object_process_line.product_id and object_process_line.product_id.uom_id.id or False,
                            #'amount' : object_process_line_sewage.amount or 0,
                            'parts_qty' : object_process_line.product_qty or 0,
                            'maintenance_id': mro_id,
                        }
                    self.pool.get('mro.order.parts.line').create(cr, uid, parts_datas)
                    self.pool.get('tms.gmao.pm.alert').validate_alert(cr, uid, object_process.alert_id.id, not object_process.periodic_done, object_process.date, object_process.km)
                    mro_ids = self.pool.get('mro.order').search(cr, uid, [('alert_id','=',object_process.alert_id.id),('state','=','draft')])
                    self.pool.get('mro.order').action_confirm(cr, uid, mro_ids)
        return {'type': 'ir.actions.act_window_close'}
    
    def action_cancel(self,cr,uid,ids,context={}):
        return {'type': 'ir.actions.act_window_close'} 
    
tms_gmao_pm_alert_process()

class tms_gmao_pm_alert_process_line(osv.osv_memory):
    u"""Traitement des lignes d'alerte"""
    _name = "tms.gmao.pm.alert.process.line"
    _description = u"Traitement ligne d'alerte"
    
    _columns = {
            'process_id' : fields.many2one('tms.gmao.pm.alert.process', u'Bon de maintenance'),
            'product_id' : fields.many2one('product.product', u'Produit', domain="[('spare_ok','=',True)]", required=True),
            'product_qty' :fields.float(u'Quantité'),
            'amount' : fields.float(u'Coût',required=True),
            'description' : fields.char(u'Description', size=50),
            }
    _defaults = {  
        'amount' : lambda *a: 0,
        }

    def onchange_product_id(self,cr,uid,ids,product_id,context={}):
        u"""évènements lors du change de produit"""
        data={}
        if product_id:
            object_product=self.pool.get('product.product').browse(cr,uid,product_id)
            if object_product:
                data['amount']=object_product.standard_price or 0
        return {'value' : data}  
    
tms_gmao_pm_alert_process_line()
