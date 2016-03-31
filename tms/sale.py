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
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from datetime import datetime
import time
from openerp import netsvc
#from months import MONTHS

__author__ = "NEXTMA"
__version__ = "0.1"
__date__ = "02 janvier 2014"

class sale_order(osv.osv):

    _name = "sale.order"
    _inherit = 'sale.order'
    _description = u"Commande voyage"

    def action_button_confirm(self, cr, uid, ids, context=None):
        assert len(ids) == 1, 'Cette option doit être utilisé pour seuleument un id à la fois.'
        wf_service = netsvc.LocalService('workflow')
        wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
 
        # redisplay the record as a sales order
        if context.get('default_travel_ok', False):
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'tms', 'view_sale_order_form_tms')
        else:
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _(u'Bon de commande'),
            'res_model': 'sale.order',
            'res_id': ids[0],
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def copy_quotation(self, cr, uid, ids, context=None):
        id = self.copy(cr, uid, ids[0], context=None)
        if context.get('default_travel_ok', False):
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'tms', 'view_sale_order_form_tms')
        else:
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bon de commande'),
            'res_model': 'sale.order',
            'res_id': id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def action_wait(self, cr, uid, ids, context=None):
        context = context or {}
        for o in self.browse(cr, uid, ids):
            if not o.order_line:
                raise osv.except_osv(_('Error!'),_('You cannot confirm a sales order which has no line.'))
            noprod = self.test_no_product(cr, uid, o, context)
            if (o.order_policy == 'manual') or noprod:
                self.write(cr, uid, [o.id], {'state': 'manual', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            else:
                self.write(cr, uid, [o.id], {'state': 'progress', 'date_confirm': fields.date.context_today(self, cr, uid, context=context)})
            self.pool.get('sale.order.line').button_confirm(cr, uid, [x.id for x in o.order_line])
        return True

    _columns = {
        'travel_ok': fields.boolean(u'voyage'),
        'boat': fields.char(u'Bateau', size=50),
        'date_end': fields.date(u'Date Fin'),          
       }

    _defaults = {
        'travel_ok': lambda *a: False,
        }

sale_order()

class sale_order_line(osv.osv):

    _name = "sale.order.line"
    _inherit = 'sale.order.line'

    def onchange_travel_return(self, cr, uid, ids, travel_return, product_id, context={}):
        u"""évènement lors du choix du trajet aller-retour"""
        data={}
        if product_id:
            traject = self.pool.get('product.product').browse(cr, uid, product_id, context)
            km_return = 0.0
            freeway_return = 0.0
            km_additional = 0.0
            freeway_additional = 0.0
            if travel_return:
                km_return = traject.km_estimated
                freeway_return = traject.freeway_estimated
                km_additional = 0.0
                freeway_additional = 0.0
            data={
                    'km_additional': km_additional,
                    'freeway_return': freeway_return,
                    'km_return': km_return,
                    'freeway_additional': freeway_additional,
                    }
        return {'value': data}

    def product_id_change_travel(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, merchandise_id=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('Aucun client défini !'), _('Avant de choisir un trajet,\n veuillez sélectionner un client dans le formulaire du bon de commande.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        if product_obj.trajet_ok==True:
            result['freeway_estimated']=product_obj.freeway_estimated or 0.0
            result['km_estimated']=product_obj.km_estimated or 0.0
        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('Vous devez sélectionner une liste de prix ou un client dans le formulaire du bon de commande !\n'
                    'Veuillez en sélectionner un avant de choisir un trajet.')
            warning_msgs += _("Aucune liste de prix ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get_travel(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, merchandise_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            data_commission = self.pool.get('product.pricelist').commission_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            commission = data_commission['commission']
            commission_value_type = data_commission['commission_value_type']
            commission_fixed = data_commission['fixed']
            if price is False:
                warn_msg = _(u"Impossible de trouver une liste de prix correspondant au trajet et à la quantité renseignés.\nVous devez changer le trajet, la quantité ou la liste de prix.")
                warning_msgs += _(u"Aucune ligne de liste de prix valide ! :") + warn_msg +"\n\n"
            else:
                data_value_commission=self.onchange_price_unit(cr, uid, ids, price, qty, commission_fixed, commission_value_type)
                if data_value_commission.get('value', False):
                    if data_value_commission['value'].get('commission', False):
                        commission = data_value_commission['value']['commission']
                result.update({'price_unit': price, 'commission': commission, 'commission_value_type': commission_value_type, 'commission_fixed': commission_fixed})
        if warning_msgs:
            warning = {
                       'title': _(u'Erreur de configuration !'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}

    def onchange_price_unit(self,cr,uid,ids,price_unit,product_uom_qty,commission_fixed,commission_value_type,context={}):
        u"""évènement lors du changement du prix unitaire"""
        data={
              'commission' : 0, 
              }
        if (price_unit or price_unit == 0) and (commission_fixed or commission_fixed == 0) and (commission_value_type or commission_value_type == 0):
            if commission_fixed == True:
                data['commission'] = commission_value_type
            else:
                data['commission'] = float(price_unit * product_uom_qty * commission_value_type) / 100
        return {'value' : data}

    def _get_total(self, cr, uid, ids, prop, unknow_none, context):
        u"""Calcul du total des km et frais d'autoroute"""
        data={}
        if ids:
            for record in self.read(cr, uid, ids, ['km_estimated', 'km_return', 'km_additional', 'freeway_estimated', 'freeway_return', 'freeway_additional'], context):
                data[record['id']]={
                                    'km_total' : 0.0,
                                    'freeway_total' : 0.0,
                                    }
                data[record['id']]['km_total'] = (record['km_estimated'] + record['km_return'] + record['km_additional']) or 0.0
                data[record['id']]['freeway_total'] = (record['freeway_estimated'] + record['freeway_return'] + record['freeway_additional']) or 0.0
        return data

    _columns = {
        'commission_fixed': fields.boolean(u'Commission fixe'),
        "travel_return": fields.boolean(u'Aller-retour',help=u"cochez cette option si vous effectuez un voyage aller-retour pour définir le km retour et les frais d'autoroute retour"),
        'km_estimated': fields.float(u"Kilomètres estimés", help=u"Kilomètres estimés définis dans la fiche trajet."),
        'km_return': fields.float(u"Kilomètres retour", help=u"Kilomètres retour, vous pouvez le définir si vous cochez l'option voyage aller-retour."),
        'km_additional': fields.float(u"Kilomètres supplémentaires", help=u"Kilomètres supplémentaires si il y'a plus que les kilomètres estimés."),
        'freeway_estimated': fields.float(u"Autoroute", help=u"Frais d'autoroute"),
        'freeway_return': fields.float(u"Autoroute retour", help=u"Frais d'autoroute en cas de voyage retour."),
        'freeway_additional': fields.float(u"Autoroute supplémentaire", help="Surplus sur les frais d'autoroute estimés."),
        'commission': fields.float(u'Commission'),
        'commission_value_type': fields.float(u'Valeur commission'),
        'consumption_gasoil': fields.float(u"Consommation gasoil %"),
        'date_end': fields.datetime(u'Date fin voyage'),
        'km_total': fields.function(_get_total, method=True, string=u'Km total', type='float', multi='sums'),
        'freeway_total': fields.function(_get_total, method=True, string=u'Frais autoroute total', type='float', multi='sums'),
        'travel_ok': fields.related('order_id', 'travel_ok', type="boolean", string=u'voyage'), 
        'merchandise_id': fields.many2one('tms.travel.palet.merchandise', string=u'Type de transport', help=u"Définissez le type de transport associé à ce voyage(ex: maïs, 1-2 Tonnes)."),
        }
    
    _defaults={
        'travel_ok': lambda *a: False,
        'km_estimated': lambda *a: 0,
        'commission': lambda *a: 0,
        'commission_value_type': lambda *a: 0,
        'km_additional': lambda *a: 0,
        'km_return': lambda *a: 0,
        'freeway_return': lambda *a: 0,
        'freeway_additional': lambda *a: 0,
        'freeway_estimated': lambda *a: 0,
        'commission_fixed': lambda *a: True,
        'travel_return': lambda *a: False,
        'consumption_gasoil': lambda *a: 0.0,
    }

sale_order_line()
