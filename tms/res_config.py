# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

#import logging

from openerp.osv import fields, osv
from openerp import pooler
from openerp.tools.translate import _

#_logger = logging.getLogger(__name__)


class tms_config_wizard(osv.osv_memory):
    _name = 'tms.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        #'default_foo': fields.type(..., default_model='my.model'),
        'tms_param_only_travel': fields.boolean(u'Permettre la création de bons carburants internes sans voyages', group='base.group_user', implied_group=''),
        'tms_param_include_tax': fields.boolean(u'Inclure les taxes de voyages dans les coûts des véhicules', group='base.group_user', implied_group=''),
        'tms_param_gasoil_external_include_tax': fields.boolean(u'Inclure les taxes de gasoil externe dans les coûts des véhicules', group='base.group_user', implied_group=''),
        'tms_param_commission_include': fields.boolean(u'Amputer les commissions dans les coûts des véhicules', group='base.group_user', implied_group=''),
        'tms_param_freeway_include': fields.boolean(u'Amputer les frais d\'autoroute dans les coûts des véhicules', group='base.group_user', implied_group=''),
        'tms_param_travel_situation': fields.boolean(u'Considérer les bons de livraisons non validés comme des voyages en cours', group='base.group_user', implied_group=''),
        'tms_param_customer_merchandise_select': fields.boolean(u'Sélection des marchandises transportées dans le formulaire des clients', group='base.group_user', implied_group=''),
        'display_tms_cost' :  fields.boolean('Gérer les frais annexes'),
        'required_vin' :  fields.boolean('Numéro de chassis obligatoire'),
        #'': fields.boolean(u'', group='base.group_user', implied_group=''),
        #'': fields.boolean(u'', group='base.group_user', implied_group=''),
        #'module_baz': fields.boolean(...),
        #'other_field': fields.type(...),
        }

    _defaults = {
        'tms_param_only_travel': lambda *a:True,
        'tms_param_include_tax': lambda *a:True,
        'tms_param_gasoil_external_include_tax': lambda *a:True,
        'tms_param_travel_situation': lambda *a:True,
        'display_tms_cost':lambda *a:False,
        'required_vin':lambda *a:False,
        #'tms_param_travel_uniq_order': lambda *a:True, @FIXME add the param in the column first
        }

    def execute(self,cr,uid,ids,context=None):
        picking_obj = self.pool.get('tms.picking')
        vehicle_obj = self.pool.get('fleet.vehicle')
        picking_ids = picking_obj.search(cr,uid,[(1,'=',1)])
        vehicle_ids = vehicle_obj.search(cr,uid,[(1,'=',1)])
        for conf in self.browse(cr,uid,ids):
            picking_obj.write(cr,uid,picking_ids,{'display_tms_cost':conf.display_tms_cost})
            vehicle_obj.write(cr,uid,vehicle_ids,{'required_vin':conf.required_vin})
        return super(tms_config_wizard,self).execute(cr,uid,ids,context=context)
    
    def _get_tms_setting_default_values(self,cr,uid,fields_name,context=None):
        setting_id = self.search(cr,uid,[(1,'=',1)],limit=1,order='id desc')
        setting = self.browse(cr,uid,setting_id)
        res = {}
        for seting in setting:
            res = self.read(cr, uid, seting.id,fields_name,context)
        return res

    def _get_tms_setting_default_values2(self,cr,uid,fields_name=['display_tms_cost'],context=None):
        setting_id = self.search(cr,uid,[(1,'=',1)],limit=1,order='id desc')
        setting = self.browse(cr,uid,setting_id)
        res = {}
        for seting in setting:
            res = self.read(cr, uid, seting.id,fields_name,context)
            return res['display_tms_cost']
tms_config_wizard()
