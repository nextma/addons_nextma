# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################
from openerp.osv import fields, osv
#import time
#from openerp import netsvc
#import datetime
from openerp.tools.translate import _

__author__ = "NEXTMA"
__version__ = "0.1"
#__date__ = u"22 Décembre 2013"

class product_product(osv.osv):
    _name = 'product.product'
    _inherit = 'product.product'
    
    def create(self, cr, uid, data, context=None):
        if ('trajet_ok' in data):
            if not  ((data['percent_rate_commission'] >= 0) and (data['percent_rate_commission'] <= 100)):
                raise osv.except_osv(u'Pourcentage invalide', u'Veuillez saisir un pourcentage entre 0 et 100')
        return super(product_product, self).create(cr, uid, data, context)
    
    def onchange_trajet_ok(self,cr,uid,ids,trajet_ok,context={}):
        u"""évènement lors du changement de trajet"""
        if trajet_ok:
            return {"value":{'type':'service', 'picking_product_ok': False, 'gasoil_ok': False, 'sale_ok': True, 'purchase_ok':False}} 
        return {"value":{}}
    
    def onchange_gasoil_ok(self,cr,uid,ids,gasoil_ok,context={}):
        u"""évènement lors du changement de la case gasoil"""
        if gasoil_ok:
            return {"value":{'type':'product', 'picking_product_ok': False, 'trajet_ok': False, 'purchase_ok': True}}
        return {"value":{}}

    def onchange_picking_product_ok(self,cr,uid,ids,picking_product_ok,context={}):
        u"""évènement lors du changement de la case gasoil"""
        if picking_product_ok:
            return {"value":{'type':'product', 'gasoil_ok': False, 'trajet_ok': False, 'purchase_ok': True}}
        return {"value":{}}
        
    def onchange_fixed_commission_ok(self,cr,uid,ids,fixed_commission_ok,context=None):
        u"""évènement lors du changement du type de commission à la commission fixe"""
        if fixed_commission_ok:
            return {'value': {'percent_commission_ok': False}}
        else:
            return {'value': {'percent_commission_ok': True}}
        
    def onchange_percent_commission_ok(self,cr,uid,ids,percent_commission_ok,context=None):
        u"""évènement lors du changement du type de commission à la commission par pourcentage"""
        if percent_commission_ok:
            return {'value': {'fixed_commission_ok': False}}
        else:
            return {'value': {'fixed_commission_ok': True}}
        
    def onchange_percent_rate_commission(self,cr,uid,ids,percent_rate_commission,context=None):
        """évènement lors du changement de la commission par pourcentage"""
        if not  ((percent_rate_commission >= 0) and (percent_rate_commission <= 100)):
            raise osv.except_osv(u'Pourcentage invalide', u'Veuillez saisir un pourcentage entre 0 et 100')
	return {}
    
    _columns = {
        'percent_commission_ok' : fields.boolean(u'Commission pourcentage'),
        'fixed_commission_ok' : fields.boolean(u'Commission fixe'),
        'trajet_ok': fields.boolean(u'trajet', help=u"Cochez cette case si vous définissez un trajet"),
        'gasoil_ok': fields.boolean(u'gasoil', help=u"Cochez cette case si vous définissez un carburant"),
        'km_estimated': fields.float(u'kilometrage estimé', digits=(16,2), help=u"km estimé du trajet"),
        'freeway_estimated': fields.float(u"Frais autoroute estimé", digits=(16,2), help=u"frais occassionnés sur l'autoroute (ex: point de péage)"),
        'driver_move_costs': fields.float(u"Frais de déplacement", digits=(16,2)),
        'driver_travel_costs': fields.float(u"Frais de déplacement", digits=(16,2)),
        'gasoil_estimated':fields.float(u'Litrage estimé', digits=(16,2), help=u"Litrage carburant estimé"),
        'rate_commission':fields.float(u'Commission trajet', digits=(16,2), help=u"Commission standard fixe"),
        'percent_rate_commission':fields.float(u'Pourcentage Commission trajet', digits=(16,2), help=u"Pourcentage commission standard"),
        'picking_customer_id': fields.many2one('res.partner', u'Client marchandise transportées'),
        'picking_product_ok': fields.boolean(u'March. transp.'),
        'cout': fields.boolean('Charges?'),
    }
    
    def unlink(self, cr, uid, ids, context=None):
        self.write(cr,uid,ids,{'active' : False})
        return True   
    
    def get_base_commission(self,cr,uid,ids,context=None):
        u"""Calculer la commission de base"""
        data_commission={
                         'fixed' : False,
                         'commission_value_type' : 0,
                         'commission' : 0,
                         }
        if ids:
            object_product=self.browse(cr,uid,ids)
            if object_product:
                if object_product.fixed_commission_ok:
                    data_commission['fixed'] = True
                    data_commission['commission_value_type'] = object_product.rate_commission
                    data_commission['commission'] = object_product.rate_commission
                    return data_commission
                elif object_product.percent_commission_ok:
                    data_commission['fixed'] = False
                    data_commission['commission_value_type'] = object_product.percent_rate_commission
                    data_commission['commission'] = object_product.rate_commission
                    if object_product.price:
                        data_commission['commission'] = (object_product.price * object_product.percent_rate_commission) / 100
                        return data_commission
                    else:
                        return data_commission 
        return data_commission 
    
    _defaults = {
        'freeway_estimated' : lambda *a: 1.0,
        'km_estimated' : lambda *a: 1.0,
        'purchase_ok' : lambda *a: 0,
        'trajet_ok' : lambda *a: False,
        'gasoil_ok' : lambda *a: False,
        'fixed_commission_ok' : lambda *a: True,
        'percent_commission_ok' : lambda *a: False,
        'percent_rate_commission' : lambda *a : 1,
        'rate_commission' : lambda *a : 0,
        'driver_move_costs': lambda *a : 0,
        'driver_travel_costs': lambda *a : 0,
        #'type' : 'service',
    }

product_product()



class product_uom(osv.osv):
    _name = 'product.uom'
    _inherit = 'product.uom' 
    _columns = {
        'travel_ok' : fields.boolean(u'unité de voyage ?', help=u"Cochez cette option si celle-ci est une unité de voyage, la quantité attribuée sera prise en compte pour les traitements multi-voyages"),
    }

    _defaults = {
        'travel_ok' : lambda *a: False,
    }

product_uom()
