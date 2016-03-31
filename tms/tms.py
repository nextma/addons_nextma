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
from cookielib import MONTHS
from datetime import datetime
import time

from openerp import netsvc, api
import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv
from openerp.tools.translate import _


#from months import MONTHS
__author__ = "NEXTMA"
__version__ = "0.1"
__date__ = u"30 décembre 2013"

class tms_picking_cost(osv.osv):
    _name = "tms.picking.cost"

    def _get_amount_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for cost in self.browse(cr, uid, ids, context=context):
            res[cost.id] = cost.price_unit*cost.quantity
        return res

    _columns = {
        'product_id': fields.many2one('product.product',u'Produit',domain="[('cout','=',True)]",required=True),
        'description' : fields.text('Description'),
        'price_unit': fields.float(u'Prix unitaire'),
        'quantity':fields.float('Quantité'),
        'discount': fields.float('Remise (%)', digits_compute= dp.get_precision('Discount')),
        'price_subtotal': fields.function(_get_amount_total, digits_compute=dp.get_precision('Account'), string='Total'),
        'picking_id':fields.many2one('tms.picking','Tms picking'),
    }
    _defaults={
            'quantity':1,
            }
    def onchange_product_id(self,cr,uid,ids,param=False):
        product = self.pool.get('product.product').browse(cr,uid,param)
        return {'value':{'price_unit':product.lst_price,'decription':product.name}}
class tms_journal(osv.osv):
    _name = "tms.journal"
    _description = "Journal TMS"
    _columns = {
        'name': fields.char(u'Journal TMS', size=32, required=True),
        'user_id': fields.many2one('res.users', u'Responsable'),
    }
    _defaults = {
        'user_id': lambda s, c, u, ctx: u,
    }

tms_journal()
class account_invoice(osv.osv):
    _inherit = 'account.invoice'
    _columns = { 
               'bl_id':fields.one2many('tms.picking','invoice_id', 'BL',ondelete="set null"),
    }

    def open_bls(self, cr, uid, ids, context=None):
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        result = mod_obj.get_object_reference(cr, uid, 'tms', 'view_tms_picking_tree')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)
        #compute the number of invoices to display
        bl_ids = []
        for so in self.browse(cr, uid, ids, context=context):
            bl_ids += [int(bl.id) for bl in so.bl_id]
        res="["
        for bl_id in bl_ids:
            res+=str(bl_id)
            res+=','
        res+="]"
        k=1
        #choose the view_mode accordingly
        if len(bl_ids)>=1:
            result['domain'] = "[('id','in',[".join(map(str, bl_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'tms', 'view_tms_picking_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = bl_ids and bl_ids[0] or False
        return result

 

account_invoice()

class tms_picking_folder(osv.osv):
    u"""Dossier de traitement de bon de livraison par lot"""
    _name="tms.picking.folder"
    _description = u'Dossier de bons de livraisons'
    
    def copy(self, cr, uid, id, default=None, context={}):
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = "%s" %(self.pool.get('ir.sequence').get(cr,uid,'tms.picking.folder'))
        default['picking_ids'] = []
        default['state'] = 'draft'
        return super(tms_picking_folder, self).copy(cr, uid, id, default, context)     
    
    _columns = {
            'name' : fields.char(u'Numéro', size=50, help=u"Nom du dossier, par défaut, il est numéroté"),
            'picking_ids' : fields.one2many('tms.picking', 'folder_id', u'Bons de livraisons', ondelete="set null"),
            'description' : fields.text(u'Description'),
            'state' : fields.selection([('draft',u'Ouvert'), ('done',u'Fermé')], u'statut', readonly=True, required=True, help=u"Les états ouvert et fermé vous permettent de savoir l'état de traitement par dossier"),
            }
    
    _defaults={
              'name' : lambda x, y, z, c: x.pool.get('ir.sequence').get(y, z,'tms.picking.folder'),
              'state' : lambda *a: 'draft',
              }
    
    def action_close_folder(self, cr, uid, ids, context={}):
        u"""fermeture de dossier"""
        if ids:
            for folder in self.browse(cr, uid, ids):
                res_folder=self.write(cr, uid, [folder.id], {'state':'done'})
                if res_folder:
                    data_obj = self.pool.get('ir.model.data')
                    res = data_obj.get_object_reference(cr, uid, 'tms', 'tms_picking_folder_form')
                    context.update({'view_id': res and res[1] or False})
                    message =u"Le dossier %s a été fermé." %folder.name
                    self.log(cr, uid, folder.id, message, context=context)
        return True
    
    def action_open_folder(self, cr, uid, ids, context={}):
        u"""ouverture de dossier"""
        if ids:
            for folder in self.browse(cr, uid, ids):
                res_folder = self.write(cr, uid, ids, {'state':'draft'})
                if res_folder:
                        data_obj = self.pool.get('ir.model.data')
                        res = data_obj.get_object_reference(cr, uid, 'tms', 'tms_picking_folder_form')
                        context.update({'view_id': res and res[1] or False})
                        message =u"Le dossier %s a été ouvert." %folder.name
                        self.log(cr, uid, folder.id, message, context=context)
        return True
    
    def action_invoice(self, cr, uid, ids, context=None): #@TODO change the method
        """ Test whether the move lines are canceled or not.
        @return: True or False
        """
        for folder in self.browse(cr, uid, ids, context=context):
            if folder.picking_ids:
                context.update({'active_ids' : [ pick.id for pick in folder.picking_ids],'active_model' : 'stock.picking'})
                return {
                    'name': u"Créer Facture du dossier %s" %folder.name,
                    'view_mode': 'form',
                    'view_id': False,
                    'view_type': 'form',
#                    'res_model': 'stock.invoice.onshipping',
#                    'res_id': partial_id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'new',
                    'domain': '[]',
                    'context': context,
                }
                
        return True
    
    _sql_constraints = [
        ('name_folder_uniq', 'unique(name)', u'Le numéro de dossier doit être unique.'),
    ]

tms_picking_folder()

class tms_picking(osv.osv):
    _name = "tms.picking"
    _inherit = ['mail.thread']
    _description = u"Bon de livraison voyage"
    _order = "date desc"

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        data = {}
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id)
            data.update({'partner_invoiced_id': partner.partner_invoiced_id.id})
        return {'value': data}
    def attachment_tree_view(self, cr, uid, ids, context):
        domain = [('res_model', '=', 'tms.picking'), ('res_id', 'in', ids)]
        res_id = ids and ids[0] or False
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'tree,form',
            'view_type': 'form',
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, res_id)
        }
    def copy(self, cr, uid, id, default=None, context=None):
        if not default:
            default = {}
        default.update({
            'name': self.pool.get('ir.sequence').get(cr, uid, 'tms.picking'),
            'origin' : '',
        })
        return super(tms_picking, self).copy(cr, uid, id, default, context=context)


    def create(self, cr, uid, vals, context=None):
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'tms.picking') or '/'
        res = super(tms_picking, self).create(cr, uid, vals, context=context)
        picking = self.browse(cr,uid,res)
        self.onchange_delivrery_qty(cr, uid, res,picking.delivrery_qty,picking.partner_id.id,picking.product_id.id,picking.merchandise_id.id,picking.uom_delivrery_id.id,picking.fixed)
        return res
 
    def onchange_date_travel(self, cr, uid, ids, date, date_end, context=None):
        u"""évènement lors du changement de date voyage"""
        data={}
        if date:
            if (not date_end) or (date_end < date):
                data['date_end'] = date
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

    def onchange_product_id(self, cr, uid, ids, partner_id=False, product_id=False, merchandise_id=False, product_qty=0.0, qty=1, context=None):
        """ On change of product id, if finds UoM, UoS, quantity and UoS quantity.
        @param partner_id: Changed Partner id
        @param product_id: Changed Product id
        @param product_id: Changed Merchandise id
        @param product_qty: Changed Product qty
        @param qty: Changed qty
        @return: Dictionary of values
        """
        if not product_id:
            return {}
        product_pool = self.pool.get('product.product')
        pricelist_pool = self.pool.get('product.pricelist')
        warning, domain = {}, {}
        partner = False
        rest= {}
        comission=0
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        else:
            raise osv.except_osv(u'Client non défini', u'Prière de selectionner un client pour l\'encodage du bon de livraison.')
        product = product_pool.browse(cr, uid, product_id, context={'lang': partner.lang})
        uos_id  = product.uos_id and product.uos_id.id or False
        result = {
            'tax_ids':  map(lambda x: x.id, product.taxes_id),
            'product_uom_id': product.uom_id.id,
            'product_uos_id': uos_id,
            'product_qty': 1.00,
            'delivrery_qty': 1.00,
            'product_uos_qty': self.onchange_quantity(cr, uid, ids, product_id, 1.00, product.uom_id.id, uos_id)['value']['product_uos_qty'],
            'qty': 1,
            'driver_move_costs': product.driver_move_costs or 0.0,
            'driver_travel_costs': product.driver_travel_costs or 0.0,
        }
        if product.uom_id:
            domain = {'product_uom_id': [('category_id', '=', product.uom_id.category_id.id)]}
            if product.uom_id.travel_ok and product_qty:
                result['qty'] = product_qty
        result['freeway_estimated']= (product.freeway_estimated or 0.0) * result.get('qty', 1)
        result['km_estimated']= (product.km_estimated or 0.0) * result.get('qty', 1)
        #commission
        if partner:
            pricelist_lst=partner.property_product_pricelist
            if pricelist_lst:
                pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
                if pricelist:
                    rest=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)
                    price=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)[pricelist]
                    comission=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission']
                    comission_is_fixe=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission_is_fixe']
                    comission_fixe=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission_fixe']

                    result['price_unit']=price
                    if not price:
                        warning = {
                            'title': u'Trajet non défini dans la liste de prix',
                            'message': u'Prière de selectionner un trajet présent dans la liste de prix du client selectionné'
                        }
                   
                    result['commission']= (comission or 0.0)
                    result['commission_is_fixe']=comission_is_fixe
                    result['commission_fixe']=comission_fixe
                else:
                    result['commission']
                    data_commission=product_pool.get_base_commission(cr,uid,product_id) 
                    result['commission'] = (data_commission['commission']) *  result.get('qty', 1)
                    result['commission_fixed'] = data_commission['fixed']
                    result['commission_value_type'] = data_commission['commission_value_type']
            else:
                data_commission=product_pool.get_base_commission(cr,uid,product_id)
                result['commission'] = data_commission['commission'] *  result.get('qty', 1)
                result['commission_fixed'] = data_commission['fixed']
                result['commission_value_type'] = data_commission['commission_value_type']
        else:
            data_commission=product_pool.get_base_commission(cr,uid,product_id)
            result['commission'] = data_commission['commission'] * result.get('qty', 1)
            result['commission_fixed'] = data_commission['fixed']
            result['commission_value_type'] = data_commission['commission_value_type']
        return {'value': result, 'warning': warning, 'domain': domain}

    def onchange_quantity(self, cr, uid, ids, product_id, product_qty, product_uom, product_uos):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_qty: Changed Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_uos_qty': 0.00
          }
        if (not product_id) or (product_qty <=0.0):
            return {'value': result}
        product_pool = self.pool.get('product.product')
        uos_coeff = product_pool.read(cr, uid, product_id, ['uos_coeff'])
        if product_uos and product_uom and (product_uom != product_uos):
            result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        else:
            result['product_uos_qty'] = product_qty
        return {'value': result}

    def onchange_uos_quantity(self, cr, uid, ids, product_id, product_uos_qty,
                          product_uos, product_uom):
        """ On change of product quantity finds UoM and UoS quantities
        @param product_id: Product id
        @param product_uos_qty: Changed UoS Quantity of product
        @param product_uom: Unit of measure of product
        @param product_uos: Unit of sale of product
        @return: Dictionary of values
        """
        result = {
                  'product_qty': 0.00
          }

        if (not product_id) or (product_uos_qty <=0.0):
            result['product_uos_qty'] = 0.0
            return {'value': result}

        product_obj = self.pool.get('product.product')
        uos_coeff = product_obj.read(cr, uid, product_id, ['uos_coeff'])

        if product_uos and product_uom and (product_uom != product_uos):
            result['product_qty'] = product_uos_qty / uos_coeff['uos_coeff']
        else:
            result['product_qty'] = product_uos_qty
        return {'value': result}
    
    def onchange_delivrery_qty(self,cr,uid,ids,delivrery_qty,partner_id=False,product_id=False,merchandise_id=False,uom_id=False,fixed=False,context=None):
        partner_pool = self.pool.get('res.partner')
        product_pool = self.pool.get('product.product')
        version_pool = self.pool.get('product.pricelist.version')
        items_pool = self.pool.get('product.pricelist.item')
        merchandises_pool = self.pool.get('product.pricelist.item.merchandise')
        if not partner_id:
            return {}
        if not product_id:
            return {}
        if not merchandise_id:
            return {}
        if not uom_id:
            return {}
        partner = partner_pool.browse(cr,uid,partner_id)
        product = product_pool.browse(cr,uid,product_id)
        pricelist= partner.property_product_pricelist and partner.property_product_pricelist.id or False
        if pricelist:
            active_version_id = version_pool.search(cr,uid,[('pricelist_id','=',pricelist),('active','=',True)])
            item_id = items_pool.search(cr,uid,[('price_version_id','in',active_version_id),('product_id','=',product.id)])
            if fixed :
                warning = {
                            "title": _("Error de Configuration!"),
                            "message" :"La quantité de livraison ou l'unité de livraison n'est pas définie dans la liste des prix de ce client",
                            }
                merchandise_ids = merchandises_pool.search(cr,uid,[('pricelist_item_id','in',item_id),('uom_id','=',uom_id)])
                for merchandise in merchandises_pool.browse(cr,uid,merchandise_ids):
                    if delivrery_qty >= merchandise.born_inf and delivrery_qty <= merchandise.born_sup :
                        return {'value': {'product_qty': 1,'price_unit':merchandise.price}}
                return {'value': {'product_qty': 1,'price_unit':0.0},'warning':warning}
            else :
                merchandise_ids = merchandises_pool.search(cr,uid,[('pricelist_item_id','in',item_id),('merchandise_id','=',merchandise_id),('uom_id','=',uom_id)],order="id desc")
                warning = {
                            "title": _("Error de Configuration!"),
                            "message" :"Vous n'avez défini aucune liste de prix pour ce type de transport",
                            }
                if merchandise_ids:
                    merchandise = merchandises_pool.browse(cr,uid,merchandise_ids[0])
                    if merchandise.min_quantity > delivrery_qty :
                        return {'value': {'product_qty': merchandise.min_quantity,'price_unit':merchandise.price}}
                    else:
                        return {'value': {'product_qty': delivrery_qty,'price_unit':merchandise.price}}
                else :
                    return {'value': {'product_qty': delivrery_qty,'price_unit':0.0},'warning':warning}
        elif delivrery_qty :
            return {'value': {'product_qty': delivrery_qty}}    
        return {}

    def onchange_vehicle_id(self, cr, uid, ids, vehicle_id, context=None):
        u"""évènement lors du changement du véhicule"""
        data, domain = {}, {}
        if vehicle_id:
            vehicle = self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id, context=context)
            if vehicle:
                data['driver_id'] = vehicle.hr_driver_id and vehicle.hr_driver_id.id or False
                data['vehicle_code'] = vehicle.default_code
                data['consumption_gasoil'] = vehicle.consumption_gasoil or 0.0
                if vehicle.trailer_id:
                    data['trailer_id'] = vehicle.trailer_id.id
                if vehicle.merchandise_id:
                    data['merchandise_id'] = vehicle.merchandise_id.id
                elif vehicle.trailer_id:
                    data['merchandise_id'] = vehicle.trailer_id.merchandise_id and vehicle.trailer_id.merchandise_id.id or False
                if vehicle.category_id: #@TODO add tms_param merchandise match vehicle category test here
                    category_id = vehicle.category_id.id
                    merchandise_ids = self.pool.get('tms.travel.palet.merchandise').search(cr, uid, [('category_id','=',category_id)])
                    if merchandise_ids:
                        domain.update({'merchandise_id': [('id','in',merchandise_ids)]})
                        if len(merchandise_ids) == 1:
                            data.update({'merchandise_id': merchandise_ids[0]})
        return {'value' : data}
    
    def onchange_driver_id(self, cr, uid, ids, driver_id, context=None):
        u"""évènement lors du changement du chauffeur"""
        data, domain = {}, {}
        if driver_id:
            vehicle_id = self.pool.get('fleet.vehicle').search(cr,uid,[('hr_driver_id','=',driver_id)],limit=1)
            if vehicle_id:
                data['vehicle_id'] = vehicle_id[0]
        return {'value' : data}

#    def onchange_quantity_travel(self, cr, uid, ids, product_id, product_qty,product_uom, product_uos, price_unit,commission_fixed, commission_value_type, travel_return):
    def onchange_quantity_travel(self, cr, uid, ids, product_id, product_qty,product_uom, product_uos, price_unit,commission, travel_return,partner_id,merchandise_id,context=None):
        partner=False
        comission_is_fixe= False
        pricelist_pool = self.pool.get('product.pricelist')
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        if partner:
            pricelist_lst=partner.property_product_pricelist
            if pricelist_lst:
                pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
                if pricelist:
                    rest=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)
                    comission=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission']
                    comission_is_fixe=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission_is_fixe']

                    comission_fixe=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission_fixe']


        result = {
            'product_uos_qty': 0.0,
            'commission': 0.0,
            'qty': 1,
        }
        if (not product_id) or (product_qty <=0.0):
            return {'value': result}
        product_pool = self.pool.get('product.product')
        uos_coeff = product_pool.read(cr, uid, product_id, ['uos_coeff'])
        if product_uos and product_uom and (product_uom != product_uos):
            result['product_uos_qty'] = product_qty * uos_coeff['uos_coeff']
        else:
            result['product_uos_qty'] = product_qty
        if product_uom:
            object_uom = self.pool.get('product.uom').browse(cr, uid, product_uom)
            object_product = product_pool.browse(cr, uid, product_id)
            if object_uom:
                if object_uom.travel_ok:
                    result['qty'] = product_qty
              
        result['km_estimated'] = result.get('qty',1) * object_product.km_estimated
        result['freeway_estimated'] = result.get('qty',1) * object_product.freeway_estimated
        if travel_return :
            result['km_return'] = result.get('qty',1) * object_product.km_estimated
            result['freeway_return'] = result.get('qty',1) * object_product.freeway_estimated
        if comission_is_fixe == True:
            result['commission'] = round(comission_fixe)
        else:
            #result['commission'] = round((float(price_unit * product_qty * commission_value_type) / 100))
            result['commission'] = round((float(price_unit * product_qty * comission) / 100))
        return {'value': result}

    def onchange_price_unit(self,cr,uid,ids,merchandise_id,product_id,price_unit,product_qty,commission,commission_fixed,commission_value_type,partner_id,qty=1,context={}):
        u"""évènement lors du changement du prix unitaire"""
        data={
              'commission' : 0, 
              }

        partner=False
        comission_is_fixe=False
        comission=0
        pricelist_pool = self.pool.get('product.pricelist')
        if partner_id:
            partner = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        if partner:
            pricelist_lst=partner.property_product_pricelist
            if pricelist_lst:
                pricelist = partner.property_product_pricelist and partner.property_product_pricelist.id or False
                if pricelist:
                    rest=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)
                    comission=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission']
                    comission_is_fixe=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission_is_fixe']

                    comission_fixe=pricelist_pool.price_get_travel(cr, uid, [pricelist], product_id, product_qty, partner.id, merchandise_id)['comission_fixe']

        if (price_unit or price_unit == 0) and (commission_fixed or commission_fixed == 0) and (commission_value_type or commission_value_type == 0):
            if comission_is_fixe == True:
                data['commission'] = comission_fixe 
            else:
                data['commission'] = (float(price_unit * product_qty * comission) / 100)
        return {'value': data}

    def onchange_price_discount(self, cr, uid, ids, discount, price_unit, context={}):
        u"""évènement lors du changement de la remise"""
        data = {}
        if discount:
            if discount >100 or discount<0:
                raise osv.except_osv(u'Erreur', u'La remise renseignée n\'est pas correcte.')
            price_unit = price_unit - (price_unit*discount)/100
            data={
              'price_unit' : price_unit,
              }
        return {'value': data}

    def onchange_travel_km_freeway_return(self, cr, uid, ids, km_return, freeway_return, travel_return, context={}):
        u"""évènement lors du changement du type de trajet et de frais d'autroute retour"""
        data = {}
        warning = {}
        if not travel_return:
            if km_return != 0:
                warning = {
                                   'title': u'Aller-retour non activé !',
                                   'message': u'Cochez la case aller-retour pour pouvoir modifier le kilométrage retour.',
                        }
                data['km_return'] = 0
            if freeway_return != 0:
                warning = {
                                   'title': u'Aller-retour non activé !',
                                    'message': u'Cochez la case aller-retour pour pouvoir modifier les frais d\'autoroute retour.',
                        }
                data['freeway_return'] = 0
        return {'value': data, 'warning': warning}

    def onchange_travel_return(self, cr, uid, ids, km_estimated, freeway_estimated, travel_return, product_id, context={}):
        u"""évènement lors du changement du type de trajet (aller-retour)"""
        data={}
        if product_id:
            km_return = 0.0
            freeway_return = 0.0
            km_additional = 0.0
            freeway_additional = 0.0
            if travel_return:
                km_return = km_estimated or 0.0
                freeway_return = freeway_estimated or 0.0
                km_additional = 0.0
                freeway_additional = 0.0
            data={
                    'km_additional': km_additional,
                    'freeway_return': freeway_return,
                    'km_return': km_return,
                    'freeway_additional': freeway_additional,
                    }
        return {'value': data}

    def _get_total_amount(self, cr, uid, ids, prop, arg, context=None):
        data={}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        currency = user.company_id and user.company_id.currency_id  or False
        cur_pool = self.pool.get('res.currency')
        tax_pool = self.pool.get('account.tax')
        for record in self.browse(cr, uid, ids, context=context):
            data[record.id]={
                                 'amount_total_ht': 0.0,
                                 'amount_tax': 0.0,
                                 'amount_total': 0.0,
                                 }
            taxes = tax_pool.compute_all(cr, uid, record.tax_ids, record.price_unit, record.product_qty)
            data[record.id]['amount_total_ht']= taxes['total']
            data[record.id]['amount_total']= taxes['total_included']
            data[record.id]['amount_tax']= taxes['total_included'] - taxes['total']
        return data

    def _get_total(self, cr, uid, ids, prop, unknow_none, context):
        u"""calcul du total du km et des frais d'autoroute"""
        data={}
        if ids:
            for record in self.read(cr, uid, ids, ['km_estimated', 'km_return', 'km_additional','freeway_estimated', 'freeway_return', 'freeway_additional'], context):
                data[record['id']]={
                                    'km_total' : 0.0,
                                    'freeway_total' : 0.0,
                                    }
                data[record['id']]['km_total'] = (record['km_estimated'] + record['km_return'] + record['km_additional']) or 0.0
                data[record['id']]['freeway_total'] = (record['freeway_estimated'] + record['freeway_return'] + record['freeway_additional']) or 0.0
        return data

    def _get_param_customer_merchandise_select(self, cr, uid, ids, prop, unknow_none, context=None):
        param_value = self.pool.get('tms.config.settings').default_get(cr, uid, ['tms_param_customer_merchandise_select'], context)
        res = {}
        for record in self.browse(cr, uid, ids, context):
            res[record.id] = param_value
        return res
    
    def _get_total_cost(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            val = 0.0 
            for cost in picking.picking_cost_ids :
                val += cost.price_subtotal
            res[picking.id] = val + picking.amount_total_ht
        return res
    def _get_observation(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for picking in self.browse(cr, uid, ids, context=context):
            ir_model_fields_obj = self.pool.get('ir.model.fields')
            ir_model_fields_id = ir_model_fields_obj.search(cr,uid,[('model','=','tms.picking'),('name','=','origin')],limit=1)
            ir_model_fields = ir_model_fields_obj.browse(cr,uid,ir_model_fields_id)
            label = str(ir_model_fields[0].field_description)
            label = label.encode('utf-8')
            if picking.origin :
                res[picking.id] = label + ":" + picking.origin
            else :
                number_colis = str(picking.number_colis) + " Colis "
                delivrery_qty = str(picking.delivrery_qty) + " "
                mesure = picking.uom_delivrery_id.name or ""
                mesure = mesure.encode('utf-8')
                res[picking.id] = number_colis + delivrery_qty + mesure
            self.write(cr,uid,picking.id,{'note':res[picking.id]})
        return res
    _columns = { 
        'name': fields.char(u'Référence', size=64, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'origin': fields.char(u'Num. TC', size=64, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}, help=u"Référence du document d'origine.", select=True),
        'note': fields.text(u'Notes', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'tms_journal_id': fields.many2one('tms.journal', u'Journal TMS', select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),

        'state': fields.selection([
            ('draft', u'Programmé'),
            ('cancel', u'Annulé'),
            ('confirmed', u'Plannifié'),
            ('assigned', u'Affecté'),
            ('decharge',u'Déchargé'),
            ('done', u'Terminé'),
            ], u'Etat', readonly=True, select=True, track_visibility='onchange', help=u"""
            * Brouillon: Bon de livraison voyage non encore confirmé et ne sera pas plannifié tant qu'il ne sera pas confirmé.\n
            * En attente de disponibilité: En attente de disponibilité du véhicule ou du chauffeur pour effectuer le voyage.\n
            * Assigné: Véhicule et chauffeur assignés, juste en attente de la validation de l'utilisateur.\n
            * Terminé: Voyage créé, bon de livraison validé et prêt à être facturé.\n
            * Annulé: La livraison a été annulée."""
        ),

        'invoice_state': fields.selection([
            ("invoiced", u"Facturé"),
            ("2binvoiced", u"À facturer"),
            ("none", u"Non Appliquable")], u"Facturation",
            select=True, required=True, readonly=True, track_visibility='onchange'),

        'date_create': fields.datetime(u'Date d\'encodage', help=u"Date d'encodage du bon.", select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'product_id': fields.many2one('product.product', u'Trajet', required=True, select=True, domain="[('trajet_ok','=',True)]", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'partner_id': fields.many2one('res.partner', u'Client', required=True, domain=[('customer','=',True)], states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'partner_invoiced_id' : fields.many2one('res.partner',u'Client à facturer',domain=[('customer','=',True)]),
        'company_id': fields.many2one('res.company', u'Compagnie', required=True, select=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),

        'folder_id': fields.char(u'Numéro de dossier', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'removal_order': fields.char(u'Bon d\'enlèvement', size=50, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'user_id': fields.many2one('res.users', u'Responsable', readonly=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),

        'driver_move_costs': fields.float(u"Frais de déplacement", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'driver_travel_costs': fields.float(u"Frais de déplacement", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'no_order': fields.char(u'N bon', size=50, help=u"N inscrit sur le bon du client.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'vehicle_id' : fields.many2one('fleet.vehicle', string=u"Véhicule", required=True, domain=[('vehicle_ok','=',True)], states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'vehicle_code': fields.char(u'Référence véhicule', size=50, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'driver_id': fields.many2one('hr.employee', string=u"Chauffeur", required=True,  domain="[('driver_ok','=','True')]", help=u"Chauffeur dédié pour ce voyage.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'trailer_id' : fields.many2one('fleet.vehicle', string=u"Semi-remorque", domain=[('trailer_ok','=',True)], help=u"Semi-remorque dédiée pour ce voyage.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'km_estimated': fields.float(u"Kilomètres estimés", help=u"Kilomètres estimés définis dans la fiche trajet.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'km_return': fields.float(u"Kilomètres retour", help=u"Cochez l'option aller-retour pour renseingner automatiquement le kilométrage retour.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'km_additional': fields.float(u"Kilomètres supplémentaires", help=u"a renseigner pour la différence de kilométrage."),
        'km_total': fields.function(_get_total, method=True, string = u'Km total', type='float', multi='sums', readonly=True, store=True),
        'freeway_estimated': fields.float(u"Frais d'autoroute", help=u"Frais d'autoroute occasionnés par le voyage (i.e: point de péage).", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'freeway_return': fields.float(u"Frais d'autoroute retour", help=u"Cochez l'option aller-retour pour renseingner automatiquement les frais d'autoroute retour.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'freeway_additional': fields.float(u"Frais d'autoroute supplémentaires", help=u"À renseigner si présence d'un supplément de frais d'autoroute.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'freeway_total': fields.function(_get_total, method=True, string=u'Frais d\'autoroute total', type='float', multi='sums', readonly=True, store=True),
        'travel_return': fields.boolean(u'Aller-retour', help=u"Cochez cette option pour un voyage aller-retour. Le km retour et les frais d'autoroute retour seront automatiquement renseignés.", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'consumption_gasoil': fields.float(u"Consommation gasoil %", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'amount_total_ht': fields.function(_get_total_amount, type='float', method=True, string=u'Total HT', digits_compute=dp.get_precision(u'Montant Total'), multi='amount', store=True, readonly=True),
        'amount_total': fields.function(_get_total_amount, type='float', method=True, string=u'Total', digits_compute=dp.get_precision(u'Montant Total'), multi='amount', store=True, readonly=True),
        'amount_tax': fields.function(_get_total_amount, method=True, string=u'Total taxe', digits_compute=dp.get_precision(u'Montant Total'), type='float', multi='amount', store=True, readonly=True),
        'commission': fields.float(u"Commission", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'commission_fixed': fields.boolean(u'Commission fixe', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'commission_value_type': fields.float(u'Valeur de la commission selon le type.', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'date': fields.datetime(u'Date voyage', required=True, help=u"Date de début du voyage", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'date_end': fields.datetime(u'Date fin', required=True, help=u"Date de fin du voyage", states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'number_colis' :fields.integer('Nombre de colis'),
        'fixed' : fields.boolean('Prix fixe par intervalle'),
        'delivrery_qty': fields.float(u'Quantité livrée', size=50, digits_compute=dp.get_precision(u'Quantité voyage'), states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'uom_delivrery_id': fields.many2one('product.uom', u'Unité livraison', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]},required=True),
        'merchandise_id': fields.many2one('tms.travel.palet.merchandise', string=u'Type de transport', required=True, states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
        'tax_ids': fields.many2many('account.tax', 'tms_picking_tax', 'picking_id', 'tax_id', u'Taxes', states={'done':[('readonly', True)], 'cancel':[('readonly',True)]}),
	    'product_qty': fields.float(u'Quantité', digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True, states={'done': [('readonly', True)], 'cancel':[('readonly',True)]},
            help=u"Quantité de marchandise selon l'UdM."
        ),
        'product_uom_id': fields.many2one('product.uom', u'Unité de mésure', required=True, states={'done': [('readonly', True)], 'cancel':[('readonly',True)]}),
        'product_uos_id': fields.many2one('product.uom', u'Produit UoS', states={'done': [('readonly', True)], 'cancel':[('readonly',True)]}),
        'product_uos_qty': fields.float(u'Quantité (UOS)', digits_compute=dp.get_precision('Product Unit of Measure'), states={'done': [('readonly', True)], 'cancel':[('readonly',True)]}),
        'price_unit': fields.float(u'Prix Unitaire', digits_compute= dp.get_precision('Product Price'), help=u"Prix en fonction de la marchandise.", states={'done': [('readonly', True)], 'cancel':[('readonly',True)]}),
        'qty': fields.integer(u'Quantité'), #@TODO check if this field is necessary
        'picking_cost_ids':fields.one2many('tms.picking.cost','picking_id', 'Charge'),
        'total_cost': fields.function(_get_total_cost, digits_compute=dp.get_precision('Account'),store=True, string='Total hors taxe'),
        'display_tms_cost' : fields.boolean('Gérer les frais annexes'),
        'details_ids': fields.one2many('tms.picking.product.details', 'picking_id', u'Détails des articles', help=u"Détail des marchandises transportées lors de ce voyage.", states={'done': [('readonly', True)], 'cancel':[('readonly',True)]}),
        'picking_merchandise_ok': fields.function(_get_param_customer_merchandise_select, method=True, type="boolean", string=u'Sélection des marchandises'),
        'grouping_id': fields.many2one('tms.grouping', u'id groupage'),
        'discount': fields.float(u'Taux de remise(%)', digits=(16, 2), help=u"Taux de remise exprimé en pourcentage (entre 0 et 100)."),
        'grouping_ok': fields.boolean(u'provenance groupage'),
      #  'invoice_ids': fields.many2many('account.invoice', 'picking_invoice_rel', 'name', 'invoice_id', 'Invoices', readonly=True, help="This is the list of invoices that have been generated for this BL. The same BL may have been invoiced in several times (by line for example)."),
        'invoice_id': fields.many2one('account.invoice',u'Invoice'),
        'obs' : fields.function(_get_observation, type="char", string=u'Observation'),
    }

    _defaults = {
        'name': lambda self, cr, uid, context: '/',
        'display_tms_cost': lambda self, cr, uid, ctx: self.pool.get('tms.config.settings')._get_tms_setting_default_values2(cr, uid,['display_tms_cost'], ctx),
        'state': 'draft',
        'invoice_state': '2binvoiced',
        'partner_id' :False,
        'date_create': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'date_end': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'company_id': lambda self, cr, uid, c: self.pool.get('res.company')._company_default_get(cr, uid, 'tms.picking', context=c),
        'user_id': lambda obj, cr, uid, context: uid,
        #'commission_fixed' : lambda *a: False,
        'commission_value_type': lambda *a: 0.0,
        'product_qty': lambda *a: 1.0,
        'km_estimated': lambda *a: 0.0,
        'km_additional': lambda *a: 0.0,
        'km_return': lambda *a: 0.0,
        'delivrery_qty': lambda *a: 1.0,
        'freeway_return': lambda *a: 0.0,
        'freeway_additional': lambda *a: 0.0,
        'freeway_estimated': lambda *a: 0.0,
        #'travel_return' : lambda *a: False,
        'commission': lambda *a: 0.0,
        'driver_move_costs': lambda *a: 0.0,
        'driver_travel_costs': lambda *a: 0.0,
        'qty': lambda *a: 1,
        'picking_merchandise_ok': lambda self, cr, uid, ctx: self.pool.get('tms.config.settings').default_get(cr, uid, ['tms_param_customer_merchandise_select'], ctx),
    }

    _sql_constraints = [
        ('picking_name_uniq', 'unique(name)', u'Le nom du BL doit être unique !'),
    ]


    def action_mise_a_jour(self, cr, uid,ids,context=None):
        benne_ids = self.pool.get('tms.travel.palet.merchandise').search(cr, uid, [('name','=','BENNE')])
        plateau_ids = self.pool.get('tms.travel.palet.merchandise').search(cr, uid, [('name','=','PLATEAU')])
        caisse_ids = self.pool.get('tms.travel.palet.merchandise').search(cr, uid, [('name','=','CAISSE')])
        solo_ids = self.pool.get('tms.travel.palet.merchandise').search(cr, uid, [('name','=','SOLO')])
        citerne_ids = self.pool.get('tms.travel.palet.merchandise').search(cr, uid, [('name','=','CITERNE')])

        benne_pickings=self.search(cr, uid, [('merchandise_id','=',benne_ids)])
        plateau_pickings=self.search(cr, uid, [('merchandise_id','=',plateau_ids)])
        caisse_pickings=self.search(cr, uid, [('merchandise_id','=',caisse_ids)])
        solo_pickings=self.search(cr, uid, [('merchandise_id','=',solo_ids)])
        citerne_pickings=self.search(cr, uid, [('merchandise_id','=',citerne_ids)])


        for benne_picking in benne_pickings:
            obj_picking=self.browse(cr, uid, benne_picking, context=None)
            result=self.onchange_quantity_travel(cr,uid,obj_picking.id, obj_picking.product_id.id, obj_picking.product_qty,obj_picking.product_uom_id, obj_picking.product_uos_id, obj_picking.price_unit,8, obj_picking.travel_return,obj_picking.partner_id,obj_picking.merchandise_id,context=None)
            com=result['value']['commission']
            self.write(cr, uid, obj_picking.id,{'commission': com}, context=None)

        for plateau_picking in plateau_pickings:
            obj_picking=self.browse(cr, uid, plateau_picking, context=None)
            result=self.onchange_quantity_travel(cr,uid,obj_picking.id, obj_picking.product_id.id, obj_picking.product_qty,obj_picking.product_uom_id, obj_picking.product_uos_id, obj_picking.price_unit,8, obj_picking.travel_return,obj_picking.partner_id,obj_picking.merchandise_id,context=None)
            com=result['value']['commission']
            self.write(cr, uid, obj_picking.id,{'commission': com}, context=None)

        for caisse_picking in caisse_pickings:
            obj_picking=self.browse(cr, uid, caisse_picking, context=None)
            result=self.onchange_quantity_travel(cr,uid,obj_picking.id, obj_picking.product_id.id, obj_picking.product_qty,obj_picking.product_uom_id, obj_picking.product_uos_id, obj_picking.price_unit,0, obj_picking.travel_return,obj_picking.partner_id,obj_picking.merchandise_id,context=None)
            com=result['value']['commission']
            self.write(cr, uid, obj_picking.id,{'commission': com}, context=None)

        for solo_picking in solo_pickings:
            obj_picking=self.browse(cr, uid, solo_picking, context=None)
            result=self.onchange_quantity_travel(cr,uid,obj_picking.id, obj_picking.product_id.id, obj_picking.product_qty,obj_picking.product_uom_id, obj_picking.product_uos_id, obj_picking.price_unit,0, obj_picking.travel_return,obj_picking.partner_id,obj_picking.merchandise_id,context=None)
            com=result['value']['commission']
            self.write(cr, uid, obj_picking.id,{'commission': com}, context=None)


        for citerne_picking in citerne_pickings:
            obj_picking=self.browse(cr, uid, citerne_picking, context=None)
            result=self.onchange_quantity_travel(cr,uid,obj_picking.id, obj_picking.product_id.id, obj_picking.product_qty,obj_picking.product_uom_id, obj_picking.product_uos_id, obj_picking.price_unit,0, obj_picking.travel_return,obj_picking.partner_id,obj_picking.merchandise_id,context=None)
            com=result['value']['commission']
            self.write(cr, uid, obj_picking.id,{'commission': com}, context=None)

        return True

#    def draft_assign()
    def draft_assign(self, cr, uid, ids, *args):
        super(tms_picking, self).write(cr, uid, ids, {'state': 'assigned'}, context=None)
        return True



   
    def button_draft(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            wf_service.trg_delete(uid, 'tms.picking', inv_id, cr)
            wf_service.trg_create(uid, 'tms.picking', inv_id, cr)
        return True

    def action_cancel(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'cancel'})
        wf_service = netsvc.LocalService("workflow")
        for inv_id in ids:
            wf_service.trg_delete(uid, 'tms.picking', inv_id, cr)
            wf_service.trg_create(uid, 'tms.picking', inv_id, cr)
        return True
    def allow_cancel(self, cr, uid, ids, *args):
        return True

    def draft_force_done(self, cr, uid, ids, *args):
        """ Terminate picking directly from draft state.
        @return: True
        """
        #wf_service = netsvc.LocalService("workflow")
        self.force_assign(cr, uid, ids)
        self.action_done(cr, uid, ids)
        return True

    def draft_force_assign(self, cr, uid, ids, *args):
        """ Confirms picking directly from draft state.
        @return: True
        """
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            if not (pick.partner_id and pick.product_id and pick.merchandise_id):
                raise osv.except_osv(_(u'Erreur!'),_(u'Vous ne pouvez pas confirmer un BL sans partenaire, produit ou marchandise.'))
            if not (pick.driver_id and pick.vehicle_id):
                raise osv.except_osv(u'Erreur !', u'Vous devez renseigner le véhicule et le chauffeur avant de confirmer.')
            wf_service.trg_validate(uid, 'tms.picking', pick.id, 'button_confirm', cr)
        return True

    def action_confirm(self, cr, uid, ids, context=None):
        """ Confirms picking.
        @return: True
        """
        #pickings = self.browse(cr, uid, ids, context=context)
        self.write(cr, uid, ids, {'state': 'confirmed'})
        return True

    #def test_assigned(self, cr, uid, ids):
    #    """ Tests whether the picking is in assigned state or not.
    #    @return: True or False
    #    """
    #    #TOFIX: assignment of move lines should be call before testing assigment otherwise picking never gone in assign state
    #    ok = True
    #    for pick in self.browse(cr, uid, ids):
    #        if pick.state != 'assigned':
    #            ok = False
    #    return ok

    def action_assign(self, cr, uid, ids, context=None):
        """ Changes state to assigned.
        @return: List of values
        """
        todo = []
        for pick in self.browse(cr, uid, ids):
            if pick.state == 'confirmed':
                todo.append(pick.id)
        res = self.check_assign(cr, uid, todo)
        return res

    def action_decharger(self, cr, uid, ids, context=None):
        """ Changes state to assigned.
        @return: List of values
        """
        if not ids:
            return []
        self.write(cr,uid,ids[0],{'state':'decharge'})
        return True
    
    def force_assign(self, cr, uid, ids, context=None):
        """ Forces the state to assigned.
        @return: True
        """
        #todo = []
        wf_service = netsvc.LocalService('workflow')
        for pick in self.browse(cr, uid, ids, context):
            #wf_service.trg_write(uid, 'tms.picking', pick.id, cr)
            if pick.state == 'draft':
                #todo.append(pick.id)
                self.draft_force_assign(cr, uid, [pick.id])
            wf_service.trg_validate(uid, 'tms.picking', pick.id, 'button_assign', cr)
        #self.write(cr, uid, todo, {'state': 'assigned'})
        return True

    def check_assign(self, cr, uid, ids, context=None):
        pickings = []
        if context is None:
            context = {}
        for pick in self.browse(cr, uid, ids, context=context):
            if not (pick.driver_id and pick.vehicle_id):
                raise osv.except_osv(u'Erreur !', u'Vous devez renseigner le véhicule et le chauffeur avant d\'assigner le BL.')
            result = self.pool.get('hr.employee').get_travel_disponibility(cr, uid, pick.id, pick.driver_id.id, pick.date, pick.date_end)
            if not result[0]:
                raise osv.except_osv(u'Chauffeur indisponible !', u'Il se trouve à cette date sur le voyage %s.'%result[1])
            result = self.pool.get('fleet.vehicle').get_travel_disponibility(cr, uid, pick.id, pick.vehicle_id.id, pick.date, pick.date_end)
            if not result[0]:
                raise osv.except_osv(u'Véhicule indisponible !', u'Il est utilisé à cette date pour le voyage %s.'%result[1])
            else:
                pickings.append(pick.id)
        if pickings:
            wf_service = netsvc.LocalService("workflow")
            for pick_id in pickings:
                wf_service.trg_validate(uid, 'tms.picking', pick_id, 'button_assign', cr)
        return len(pickings)

    def action_assign_wkf(self, cr, uid, ids, context=None):
        """ Changes picking state to assigned.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'assigned'})
        return True
    def create_invoice(self,cr, uid, ids,partner_id_id,date_invoice=False, context=None):
        res=[]
        company_id=self.pool['res.company']._company_default_get(cr,uid,object='tms_picking',context=context)
        invoice_specs=self.pool.get('tms.picking').get_partner_account_id(cr,uid,ids,partner_id_id,company_id)

        res = self.pool.get('account.invoice').create(cr, uid, {
				'partner_id': partner_id_id,
				'date_invoice': date_invoice,
                'account_id':invoice_specs['account_id'],
				}, context=context)
        return res


    def get_product_account_id(self, cr, uid, ids, product, type='out_invoice', partner_id=False, fposition_id=False,context=None, company_id=None):
        if context is None:
            context = {}
        company_id = company_id if company_id != None else context.get('company_id',False)
        part = self.pool.get('res.partner').browse(cr, uid, partner_id, context=context)
        fpos_obj = self.pool.get('account.fiscal.position')
        fpos = fposition_id and fpos_obj.browse(cr, uid, fposition_id, context=context) or False

        result = {}
        res = self.pool.get('product.product').browse(cr, uid, product, context=context)

        if type in ('out_invoice','out_refund'):
            a = res.property_account_income.id
            if not a:
                a = res.categ_id.property_account_income_categ.id
        else:
            a = res.property_account_expense.id
            if not a:
                a = res.categ_id.property_account_expense_categ.id
        a = fpos_obj.map_account(cr, uid, fpos, a)
        if a:
            result['account_id'] = a
        return result


    def get_partner_account_id(self, cr, uid, ids, partner_id,company_id=False):

        acc_id = False

        opt = [('uid', str(uid))]
        if partner_id:

            opt.insert(0, ('id', partner_id))
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if (p.property_account_receivable.company_id and (p.property_account_receivable.company_id.id != company_id)) and (p.property_account_payable.company_id and (p.property_account_payable.company_id.id != company_id)):
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]

            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_payable.id

            else:
                acc_id = p.property_account_receivable.id

        result = {'account_id': acc_id,}

        return result



    def action_invoice_create(self, cr, uid, ids,tax_ids,product_uom_id,description,product_id,quantity,price_unit,partner_id_id, date_invoice = False, context=None):
        res=[]
        invoice = self.pool.get('account.invoice')
        account_obj = self.pool.get('account.account')
        if context is None:
            context = {}
        if date_invoice:
            context['date_invoice'] = date_invoice
        company_id=self.pool['res.company']._company_default_get(cr,uid,object='tms_picking',context=context)
        company = self.pool.get('res.company').browse(cr, uid, company_id)
        currency_id=company.currency_id.id
        invoice_specs=self.get_partner_account_id(cr,uid,ids,partner_id_id,company_id)
        invoice_id = self.pool.get('account.invoice').create(cr, uid, {
				'partner_id': partner_id_id,
				'date_invoice': date_invoice,
                'account_id':invoice_specs['account_id'],
				}, context=context)
        invoice_line_spec=self.get_product_account_id(cr, uid, ids, product_id,'out_invoice', partner_id_id, False,context, company_id)
        invoice_line_id = self.pool.get('account.invoice.line').create(cr,uid,{
                 'invoice_id':invoice_id,
                 'name':description,
                 'account_id':invoice_line_spec['account_id'],
                 'product_id':product_id,
                 'price_unit':price_unit,
                 'quantity':quantity,
                 'uos_id':product_uom_id,
                 'invoice_line_tax_id':[(6, 0, [x.id for x in tax_ids])],
                  }, context=context)

        return invoice_id
    def _get_invoice_vals(self, cr, uid, key, inv_type, journal, origin, context=None):
        journal_id = journal.id
        if context is None:
            context = {}
        partner,company_id = key
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = partner.property_account_receivable.id
            payment_term = partner.property_payment_term.id or False
        else:
            account_id = partner.property_account_payable.id
            payment_term = partner.property_supplier_payment_term.id or False
        return {
            'origin': origin,
            'date_invoice': context.get('date_inv', False),
            #'user_id': user_id,
            'partner_id': partner.id, 
            'partner_delivery_id' :context.get('partner_delivery_id'),
            'account_id': account_id,
            'payment_term': payment_term,
            'type': inv_type,
            'fiscal_position': partner.property_account_position.id,
            'company_id': company_id,
            #'currency_id': currency_id,
            #'journal_id': journal_id,
        }
    def _create_invoice_from_picking(self, cr, uid, picking, vals, context=None):
        ''' This function simply creates the invoice from the given values. It is overriden in delivery module to add the delivery costs.
        '''
        invoice_obj = self.pool.get('account.invoice')
        return invoice_obj.create(cr, uid, vals, context=context)
    def _get_invoice_line_vals(self, cr, uid, move, partner, inv_type, context=None):
        fp_obj = self.pool.get('account.fiscal.position')
        # Get account_id
        if inv_type in ('out_invoice', 'out_refund'):
            account_id = move.product_id.property_account_income.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_income_categ.id
        else:
            account_id = move.product_id.property_account_expense.id
            if not account_id:
                account_id = move.product_id.categ_id.property_account_expense_categ.id
        fiscal_position = partner.property_account_position
        account_id = fp_obj.map_account(cr, uid, fiscal_position, account_id)

        # set UoS if it's a sale and the picking doesn't have one
        uos_id = move.product_uom_id.id
        quantity = move.product_qty
        #if move.product_uos:
            #uos_id = move.product_uos.id
            #quantity = move.product_uos_qty
        return {
            'name': move.name,
            'account_id': account_id,
            'product_id': move.product_id.id,
            'uos_id': uos_id,
            'quantity': quantity,
            'price_unit': move.price_unit,
            'discount':  move.discount,
            'invoice_line_tax_id':[(6, 0, [x.id for x in move.tax_ids])],
            'merchandise_id' : move.merchandise_id.id,
            'vehicle_id': move.vehicle_id.id,
        }

    def _create_invoice_line_from_vals(self, cr, uid, move, invoice_line_vals, context=None):
        if move.fixed: 
            unit = ""
            try:
                unit = move.uom_delivrery_id.name.encode('utf-8')
            except :
                pass
            chaine = str(move.name) + " " + str(move.number_colis) + " colis " + str(move.delivrery_qty) + " " + unit
            invoice_line_vals['name'] = chaine
        return self.pool.get('account.invoice.line').create(cr, uid, invoice_line_vals, context=context)

    def _invoice_create_line(self, cr, uid, moves, journal_id, inv_type='out_invoice', context=None):
        invoice_obj = self.pool.get('account.invoice')
        invoice_line_obj = self.pool.get('account.invoice.line')
        move_obj = self.pool.get('tms.picking')
        invoices = {}
        todo = {}
        for move in moves:
            company_id = self.pool['res.company']._company_default_get(cr,uid,object='tms_picking',context=context)
            company = self.pool['res.company'].browse(cr,uid,company_id)
            origin = move.name
            if move.partner_invoiced_id:
                partner = move.partner_invoiced_id
            else :
                partner = move.partner_id
            product_id = move.product_id
            key = (partner,company.id)

            if key not in invoices:
                # Get account and payment terms
                invoice_vals = self._get_invoice_vals(cr, uid, key, inv_type, journal_id, origin, context=context)
                invoice_id = self._create_invoice_from_picking(cr, uid, move.id, invoice_vals, context=context)
                invoices[key] = invoice_id
            invoice_line_vals = move_obj._get_invoice_line_vals(cr, uid, move, partner, inv_type, context=context)
            invoice_line_vals['invoice_id'] = invoices[key]
            invoice_line_vals['origin'] = origin
            
            domain = []
            if context.get('grouped_by_product')=='travel_and_type':
                domain = [('invoice_id','=',invoices[key]),('product_id','=',move.product_id.id),('merchandise_id','=',move.merchandise_id.id),('price_unit','=',move.price_unit)]
            elif context.get('grouped_by_product')=='travel_and_vehicle':
                domain = [('invoice_id','=',invoices[key]),('product_id','=',move.product_id.id),('vehicle_id','=',move.vehicle_id.id),('price_unit','=',move.price_unit)]
            invoice_line_id = invoice_line_obj.search(cr,uid,domain,limit=1)
            
            if invoice_line_id:
                invoice_line = invoice_line_obj.browse(cr,uid,invoice_line_id)
                qty = invoice_line.quantity + move.product_qty
                invoice_line_obj.write(cr,uid,invoice_line_id,{'quantity':qty})
            else :
                move_obj._create_invoice_line_from_vals(cr, uid, move, invoice_line_vals, context=context)
            
            for cost in move.picking_cost_ids :
                invoice_line_cost_vals ={
                        'product_id' : cost.product_id.id,
                        'name' : cost.description or cost.product_id.description_sale or cost.product_id.name,
                        'price_unit': cost.price_unit,
                        'quantity' : cost.quantity,
                        'invoice_line_tax_id':[(6, 0, [x.id for x in cost.product_id.taxes_id])],
                        'discount' : cost.discount,
                        'merchandise_id' : move.merchandise_id.id,
                        'vehicle_id': move.vehicle_id.id,
                        'invoice_id' : invoices[key],
                        'origin' : origin
                        }
                cost_domain = [('invoice_id','=',invoices[key]),('product_id','=',cost.product_id.id),('price_unit','=',cost.price_unit)]
                cost_invoice_line_id = invoice_line_obj.search(cr,uid,cost_domain,limit=1)
                if cost_invoice_line_id:
                    cost_invoice_line = invoice_line_obj.browse(cr,uid,cost_invoice_line_id)
                    qty = cost_invoice_line.quantity + cost.quantity
                    invoice_line_obj.write(cr,uid,cost_invoice_line_id,{'quantity':qty})
                else :
                    move_obj._create_invoice_line_from_vals(cr, uid, move, invoice_line_cost_vals, context=context)

            move_obj.write(cr, uid, move.id, {'invoice_state': 'invoiced','invoice_id': invoices[key]}, context=context)

        invoice_obj.button_compute(cr, uid, invoices.values(), context=context, set_total=(inv_type in ('in_invoice', 'in_refund')))
        return invoices.values()
    


    def action_done(self, cr, uid, ids, context=None):
        wf_service = netsvc.LocalService("workflow")
        for pick in self.browse(cr, uid, ids):
            if pick.state == 'assigned':
                res_crea = self.pool.get('tms.travel').create(cr, uid, {
                         'picking_id': pick.id,
                         'date': pick.date or False,
                         'name': pick.name or "",
                         'vehicle_code': pick.vehicle_code or "",
                         'product_id': pick.product_id and pick.product_id.id or False,
                         'vehicle_id': pick.vehicle_id and pick.vehicle_id.id or False,
                         'trailer_id': pick.trailer_id and pick.trailer_id.id or False,
                         'driver_id': pick.driver_id and pick.driver_id.id or False,
                         'amount_total_ht': pick.amount_total_ht or 0.0,
                         'amount_total': pick.amount_total or 0.0,
                         'freeway_total': pick.freeway_total or 0.0,
                         'km_total': pick.km_total or 0.0,
                         },{'travel_ok': True})
                #@TODO check how to log messages
                #if res_crea:
                    #self.pool.get('tms.travel').log_message(cr,uid,[res_crea])
                #self.write(cr, uid, pick.id, {'state': 'done'})
                wf_service.trg_validate(uid, 'tms.picking', pick.id, 'button_done', cr)
            self.write(cr, uid, ids, {'state': 'done'})
        return True

    def action_done_wkf(self, cr, uid, ids, context=None):
        """ Changes picking state to done.
        @return: True
        """
        self.write(cr, uid, ids, {'state': 'done'})
        return True

tms_picking()

class tms_picking_product_details(osv.osv):
    _name='tms.picking.product.details'
    _description=u'Détails marchandises transportées'

    _columns={
        'picking_partner_id': fields.many2one('res.partner', invisible=True),
        'picking_id': fields.many2one('tms.picking', u'BL', required=True),
        'product_id': fields.many2one('product.product', u'Article', required=True, domain=[('trajet_ok','=',False)]),
        'description': fields.char(u'Description', size=64),
        'product_uom_id': fields.many2one('product.uom', u'Unité de mesure', required=True, help=u"Unité de mesure du produit."),
        'product_qty': fields.float(u'Quantité', required=True),
             }
    _defaults={
        'product_qty': 1.0,
        }

    def on_change_picking_partner_id(self, cr, uid, ids, picking_partner_id, context=None):
        partner_obj = self.pool.get('res.partner').browse(cr, uid, picking_partner_id, context=context)
        if not partner_obj:
            raise osv.except_osv(u'Attention !', u'Sélectionnez le client d\'abord avant d\'ajouter ses marchandises.')
        product_ids = [obj.id for obj in partner_obj.picking_merchandise_ids]
        return {'domain': {'product_id': [('id','in',product_ids)]}}

    def onchange_product_id(self, cr, uid, ids, product_id, context=None):
        data = {}
        if product_id:
            prod_datas = self.pool.get('product.product').read(cr, uid, product_id, ['uom_id', 'name'])
            data.update({'description': prod_datas['name'], 'product_uom_id': prod_datas['uom_id'][0]})
        return {'value': data}


tms_picking_product_details()

class tms_travel_palet_merchandise(osv.osv):
    u"""Type de transport ou marchandise du voyage"""
    _name = 'tms.travel.palet.merchandise'
    
    def copy(self, cr, uid, id, default=None, context={}):
        u"""méthode de copie"""
        if default is None:
            default = {}
        default = default.copy()
        default['name'] = "%s copy" %default.get('name',u'Type de transport')
        return super(tms_travel_palet_merchandise, self).copy(cr, uid, id, default, context)     
    
    _columns = {  
                'name': fields.char(u'Marchandise', size=20, required=True),
                'category_id': fields.many2one('fleet.vehicle.category', u'Catégorie de véhicule', domain=[('vehicle_ok','=',True)]),
                'description': fields.char(u'Description', size=20),
                }
    _sql_constraints = [
        ('merchandise_name_uniq', 'unique(name)', u'Le nom du type de transport doit être unique !')
    ]

tms_travel_palet_merchandise()

class tms_travel(osv.osv):
    u"""Voyage officiel"""
    
    _name = 'tms.travel'
    _description = u'Voyage'
    _order='date desc'
    
    def create(self,cr,uid,vals,context=None):
        u"""méthode de création"""
        if context:
            flag_travel=context.get('travel_ok', False)
            if flag_travel:
                data_obj = self.pool.get('ir.model.data')
                res = data_obj.get_object_reference(cr, uid, 'account', 'analytic_journal_sale')
                id_journal= res and res[1] or False
                #@TODO fix completly the param problem
                vals['tax_ok'] = False #self.pool.get('tms.param').get_value_by_reference(cr,uid,'tms','tms_param_include_tax')
                vals['commission_ok'] = True #self.pool.get('tms.param').get_value_by_reference(cr,uid,'tms','tms_param_commission_include')
                vals['freeway_ok'] = True #self.pool.get('tms.param').get_value_by_reference(cr,uid,'tms','tms_param_freeway_include')
                id_travel= super(tms_travel, self).create(cr, uid, vals, context)
                record = False
                if ('picking_id' in vals):
                    record = self.pool.get('tms.picking').browse(cr,uid,vals['picking_id'],{})
                elif ('grouping_id' in vals):
                    record = self.pool.get('tms.grouping').browse(cr,uid,vals['grouping_id'],{})
                if record:
                    price_analytiq = 0
                    if vals['tax_ok']==True:
                        price_analytiq=record.amount_total
                    else:
                        price_analytiq=record.amount_total_ht
                    if vals['commission_ok']==True:
                        price_analytiq -= record.commission
                    if vals['freeway_ok']==True:
                        price_analytiq -= record.freeway_total
                    if record.vehicle_id:
                        object_vehicle = record.vehicle_id
                        data_odometer = {
                                                      'value': object_vehicle.odometer + record.km_total, #@TODO to compute the new odometer
                                                      'vehicle_id': object_vehicle.id,
                                                      'travel_ok': True,
                                                    }
                        id_odometer1 = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data_odometer)
                        try :
                            self.write(cr, uid, [id_travel], {'vehicle_odometer_id': id_odometer1})
                        except :
                            pass
                        if object_vehicle.account_id:
                            data_account_line={
                                                        'name' : record.name,
                                                        'product_id' : vals.get('product_id', False),
                                                        'amount' : price_analytiq,
                                                        'date' : record.date,
                                                        'account_id' : object_vehicle.account_id.id,
                                                        'general_account_id' : 1,
                                                        'journal_id' : id_journal,
                                                        }
                            self.pool.get('account.analytic.line').create(cr,uid,data_account_line)
                    if record.trailer_id:
                        object_trailer = record.trailer_id
                        data_odometer = {
                                                      'value': object_trailer.odometer + record.km_total, #@TODO to compute the new odometer
                                                      'vehicle_id': object_trailer.id,
                                                      'travel_ok': True,
                                                    }
                        id_odometer2 = self.pool.get('fleet.vehicle.odometer').create(cr, uid, data_odometer)
                        self.write(cr, uid, [id_travel], {'trailer_odometer_id': id_odometer2})
                        if object_trailer.account_id:
                            data_account_line={
                                                            'name' : record.name,
                                                            'product_id' : vals.get('product_id', False),
                                                            'amount' : price_analytiq,
                                                            'date' : record.date,
                                                            'account_id' : object_trailer.account_id.id,
                                                            'general_account_id' : 1,
                                                            'journal_id' : id_journal,
                                                            }
                            self.pool.get('account.analytic.line').create(cr,uid,data_account_line)
                return id_travel
            else:
                raise osv.except_osv(_(u'Mauvaise procédure!'), _(u'Pour créer un voyage vous devez passer par le bon de commande ou le bon de livraison'))
        else:
            raise osv.except_osv(_(u'Mauvaise procédure!'), _(u'Pour créer un voyage vous devez passer par le bon de commande ou le bon de livraison'))

    def _get_month(self, cr, uid, ids, name, arg, context={}):
        u"""récupère le mois/année de la date de voyage"""
        data={}
        for object_line in self.browse(cr,uid,ids):
            data[object_line.id] = ''
            if object_line.date:
                date_month=time.strptime(object_line.date, '%Y-%m-%d %H:%M:%S')
                month=MONTHS[date_month.tm_mon-1]
                year = date_month.tm_year
                data[object_line.id]="%s-%s" %(year,month)
        return data
    
    def unlink(self, cr, uid, ids, context=None):
        u"""méthode de suppression du voyage"""
        if context==None or not context.get('travel_ok',False):
            raise osv.except_osv(u'Suppression impossible', u'Vous ne pouvez pas supprimer de voyages')
        data_obj = self.pool.get('ir.model.data')
        res = data_obj.get_object_reference(cr, uid, 'account', 'analytic_journal_sale')
        id_journal= res and res[1] or False
        for object_travel in self.browse(cr,uid,ids):
            price_analytiq = 0
            if object_travel.tax_ok==True:
                price_analytiq=object_travel.amount_total
            else:
                price_analytiq=object_travel.amount_total_ht
            if object_travel.commission_ok == True:
                price_analytiq-=object_travel.commission
            if object_travel.freeway_ok == True:
                price_analytiq -= object_travel.freeway_total
            if object_travel.vehicle_id:
                if object_travel.vehicle_odometer_id:
                    self.pool.get('fleet.vehicle.odometer').unlink(cr, uid, object_travel.vehicle_odometer_id.id)
                if object_travel.vehicle_id.account_id:
                    data_account_line={
                                        'name' : u'Annulation %s' %object_travel.name,
                                        'amount' : -1 * price_analytiq,
                                        'date' : object_travel.date,
                                        'account_id' : object_travel.vehicle_id.account_id.id or False,
                                        'general_account_id' : 1,
                                        'journal_id' : id_journal,    
                                    }
                    id_account_line=self.pool.get('account.analytic.line').create(cr,uid,data_account_line) 
            if object_travel.trailer_id:
                if object_travel.trailer_odometer_id:
                    self.pool.get('fleet.vehicle.odometer').unlink(cr, uid, object_travel.trailer_odometer_id.id)
                if object_travel.trailer_id.account_id:
                    data_account_line={
                                         'name' : u'Annulation %s' %object_travel.name,
                                         'amount' : -1 * price_analytiq,
                                         'date' : object_travel.date,
                                         'account_id' : object_travel.trailer_id.account_id.id,
                                         'general_account_id' : 1,
                                         'journal_id' : id_journal,
                                       }
                    self.pool.get('account.analytic.line').create(cr,uid,data_account_line)
        return super(tms_travel, self).unlink(cr, uid, ids, context) 

    def _get_liter_estimated(self, cr, uid, ids, prop, unknow_none, context):
        u"""calcul du litrage estimé"""
        data={}
        if ids:
            for record in self.read(cr, uid, ids, ['consumption_gasoil', 'km_return', 'km_estimated'], context):
                data[record['id']] = (record['consumption_gasoil'] * (record['km_estimated'] + record['km_return'])) / 100
        return data
    
    def _get_commission_driver(self, cr, uid, ids, prop, unknow_none, context):
        u"""calcul de la commission chauffeur"""
        data={}
        if ids:
            for record in self.browse(cr, uid, ids, context):
                data[record.id]=0.0
                if record.product_id:
                    data[record.id]=record.product_id and record.product_id.rate_commission or 0.0
        return data     

    def log_message(self,cr,uid,ids,context={}):
        u"""message de journalisation"""
        if ids:
            for object_travel in self.browse(cr,uid,ids):
                data_obj = self.pool.get('ir.model.data')
                res = data_obj.get_object_reference(cr, uid, 'tms', 'view_tms_travel_form')
                context.update({'view_id': res and res[1] or False})
                message = u"Le voyage %s a été créé" %object_travel.name
                self.log(cr, uid, object_travel.id, message, context=context)
        return True
    
    def action_move(self,cr,uid,ids,context=None):
        u"""assigner le voyage à un bon carburant"""
        gasoil_order_id=context.get('gasoil_order',False)
        if gasoil_order_id:
            object_gasoil_order=self.pool.get('tms.gasoil.order').browse(cr,uid,gasoil_order_id)
            if object_gasoil_order:
                if object_gasoil_order.state in ('progress','cancel'):
                    self.write(cr,uid,ids,{'gasoil_order':gasoil_order_id,'state':'assigned'})
        return True
    
    def name_get(self, cr, uid, ids, context=None):
        u"""Nom du voyage"""
        if not len(ids):
            return []
        reads = self.read(cr, uid, ids, ['name','vehicle_id'], context)
        res = []
        for record in reads:
            name = record['name']
            if record['vehicle_id']:
                name = record['vehicle_id'][1]+' / '+ (name or '-')
            res.append((record['id'], name))
        return res
    
    def action_cancel(self,cr,uid,ids,context=None):
        u"""annuler l'assignation du voyage au bon carburant"""
        self.write(cr,uid,ids,{'gasoil_order':False,'state':'free'})
        return True
    
    def hold(self,cr,uid,ids,context=None):
        u"""valider l'assignation du bon"""
        self.write(cr,uid,ids,{'state':'hold'})
        return True
    
    def unhold(self,cr,uid,ids,context=None):
        u"""dévalider l'assignation du bon"""
        self.write(cr,uid,ids,{'state':'assigned'})
        return True

    _columns = {
        'trailer_odometer_id': fields.many2one('fleet.vehicle.odometer', u'id1 odometer'),
        'vehicle_odometer_id': fields.many2one('fleet.vehicle.odometer', u'id2 odometer'),
        'picking_id': fields.many2one('tms.picking', u'BL associé', readonly=True),
        'grouping_id': fields.many2one('tms.grouping', u'Groupage associé', readonly=True),
        'fuel_order_id': fields.many2one('fleet.vehicle.log.fuel', string=u"Bon gasoil interne", readonly=True, help=u"Bon carburant interne associé au voyage"),
        'system_number': fields.char(u'Numéro du système', size=64, required=False, readonly=False),
        'tax_ok' : fields.boolean(u'Taxes incluses dans l\'analytique'),
        'commission_ok' : fields.boolean(u'commissions incluses dans l\'analytique'),
        'freeway_ok' : fields.boolean(u'frais autoroutes incluses dans l\'analytique'),
        'observation': fields.char(u'Observation', size=64, required=False, readonly=False),
        'state' : fields.selection([('free', u'Non assigné'),('assigned', u'assigné'),('cancel', u'annuler'),('hold', u'traité')], u'Statut',required=True, readonly=True, select=True ),
        #'month' : fields.function(_get_month,type='char',method=True,string=u"Mois"),

        # common fields
        'date': fields.datetime(string=u'Date début', readonly=True),
        'name': fields.char(type="char", readonly=True, string=u'Voyage', size=100, help=u"Nom du voyage"),
        'product_id': fields.many2one('product.product', u'Trajet', readonly=True),
        'vehicle_id': fields.many2one('fleet.vehicle', domain=[('vehicle_ok','=',True)], readonly=True, string=u'Véhicule'),
        'vehicle_code': fields.char(string=u'Référence véhicule', readonly=True, size=32),
        'driver_id': fields.many2one('hr.employee', readonly=True, string=u'Chauffeur'),
        'trailer_id': fields.many2one('fleet.vehicle', domain=[('trailer_ok','=',True)], readonly=True, string=u'Semi-remorque'),
        'km_total': fields.float(string=u"Km total", digits=(16,2), readonly=True),
        'freeway_total': fields.float(string=u"Frais autoroute total", digits=(16,2), readonly=True),
        'amount_total_ht': fields.float(string=u"Total HT", digits_compute= dp.get_precision(u'Montant Total'), readonly=True),
        'amount_total': fields.float(string=u"Total TTC", digits_compute= dp.get_precision(u'Montant Total'), readonly=True),

        # picking related fields
        'folder_id' : fields.related('picking_id', 'folder_id', string=u'Dossier', type='many2one', relation='tms.picking.folder', store=True, readonly=True),
        'product_qty': fields.related('picking_id', 'product_qty', type="float", readonly=True,string=u'Quantité facturée', store=True),
        #'address_destination' : fields.related('move_id', 'address_destination', type="many2one", readonly=True,string=u'bénéficiaire',relation='res.partner.address',store=True),
        'product_uom_id': fields.related('picking_id', 'product_uom_id', type="many2one", relation="product.uom",readonly=True,string=u'unité de mesure facturée',store=True  ),
        'driver_move_costs': fields.related('picking_id','driver_move_costs',type='float',string=u"Frais de déplacement",digits=(16,2),store=True,readonly=True),
        'driver_travel_costs': fields.related('picking_id','driver_travel_costs',type='float',string=u"Frais de voyage",digits=(16,2),store=True,readonly=True),
        'consumption_gasoil': fields.related('picking_id', 'consumption_gasoil', type='float', string=u'Consommation gasoil %',store=True, readonly=True),
        'km_estimated': fields.related('picking_id','km_estimated',type='float',string=u"Km estimé",digits=(16,2),store=True,readonly=True),
        'km_additional': fields.related('picking_id','km_additional',type='float',string=u"Km supplémentaire",digits=(16,2),store=True,readonly=True),
        'km_return': fields.related('picking_id','km_return',type='float',string=u"Km retour",digits=(16,2),store=True,readonly=True),
        'liter_estimated':fields.function(_get_liter_estimated, method=True, type="float", string=u"Litrage estimé",store=True),
        'partner_id' : fields.related('picking_id', 'partner_id', type="many2one", relation="res.partner",readonly=True,string=u'Client',store=True ),
        'origin' : fields.related('picking_id', 'origin', type="char",readonly=True,string=u'Bon de commande',store=True),
        'freeway_estimated': fields.related('picking_id','freeway_estimated',type='float',string=u"Frais autoroute estimé",digits=(16,2),store=True,readonly=True),
        'freeway_additional': fields.related('picking_id','freeway_additional',type='float',string=u"Frais autoroute supplémentaires",digits=(16,2),store=True,readonly=True),
        'freeway_return': fields.related('picking_id','freeway_return',type='float',string=u"Frais autoroute retour",digits=(16,2),store=True,readonly=True),
        "travel_return": fields.related('picking_id', 'travel_return', type="boolean",readonly=True,string=u'Aller-retour', store=True),                
        #'date': fields.related('picking_id','date',type='datetime',string=u'date début',store=True,readonly=True),
        #'date_end': fields.related('picking_id','date_end',type='datetime',string=u'date fin',store=True,readonly=True),
        'qty': fields.related('picking_id','qty',string='quantité', type="integer"),
        #'amount_total_ht' : fields.related('picking_id','amount_total_ht',type='float',string=u"Total HT", digits_compute= dp.get_precision(u'Montant Total'),store=True,readonly=True),
        #'amount_total': fields.related('picking_id','amount_total',type='float',string=u"Total TTC", digits_compute= dp.get_precision(u'Montant Total'),store=True,readonly=True),
        'amount_tax' : fields.related('picking_id','amount_tax',type='float',string=u"Total TAX", digits_compute= dp.get_precision(u'Montant Total'),store=True,readonly=True),
        'commission_driver' : fields.related('picking_id', 'commission', type="float",readonly=True,string=u'commission',store=True ) ,
        'no_order' : fields.related('picking_id', 'no_order', type="char",string=u'N° bon',size=50,readonly=True,store=True ) ,
        'removal_order' : fields.related('picking_id','removal_order',string=u'Bon d\'enlèvement',type='char',store=True),     
        'delivrery_qty' : fields.related('picking_id', 'delivrery_qty', type="float",readonly=True,string=u'quantité livrée', store=True) ,
        'uom_delivrery_id' : fields.related('picking_id', 'uom_delivrery_id', type="many2one",readonly=True,string=u'unité livraison',relation='product.uom',store=True),
        'merchandise_id' : fields.related('picking_id','merchandise_id', type='many2one', relation='tms.travel.palet.merchandise', string=u'Type de transport', readonly=True,store=True),
        }
    
    _defaults = {
        'no_order' : lambda *a: u'/',
        'state':lambda *a: 'free',
        'km_estimated':lambda *a: 0,
        'km_additional': lambda *a:0,
        'km_return': lambda *a:0,
        'km_estimated': lambda *a:0,
        'km_additional':lambda *a: 0,
        'km_return': lambda *a:0,
        'tax_ok' :lambda *a: False, 
        'commission_ok' :lambda *a: False, 
        }

tms_travel()

