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

from openerp.osv import fields, osv, orm
import openerp.addons.decimal_precision as dp
from openerp.tools.translate import _
from openerp import tools

__author__ = "NEXTMA"
__version__ = "0.1"
__date__ = "13 janvier 2014"

class log_fuel_external_card(osv.osv_memory):
    _name = 'log.fuel.external.card'
    _description = 'Carte de gasoil externe'

    def default_get(self, cr, uid, fields, context=None):
        if context is None: 
            context = {}
        res = super(log_fuel_external_card, self).default_get(cr, uid, fields, context=context)
        internal_order_ids = context.get('active_ids', [])
        if not internal_order_ids or len(internal_order_ids) != 1 or context.get('active_model', "") != 'fleet.vehicle.log.fuel':
            # one internal id at a time
            return res
        datas = self.pool.get('fleet.vehicle.log.fuel').read(cr,uid,internal_order_ids[0], ['date_order', 'vehicle_id', 'vehicle_code', 'driver_id', 'owner', 'manager', 'company_id'])
        res.update({
            'internal_order_id': internal_order_ids[0],
            'date_order': datas['date_order'] or time.strftime('%Y-%m-%d %H:%M:%S'),
            'driver_id': datas['driver_id'] and datas['driver_id'][0] or False,
            'owner': datas['owner'] or "", #and datas['owner_id'][0] or False,
            'manager': datas['manager'] or "", #and datas['manager_id'][0] or False,
            'vehicle_code': datas['vehicle_code'] or False,
            'vehicle_id': datas['vehicle_id'] and datas['vehicle_id'][0] or False,
            'company_id': datas['company_id'] and datas['company_id'][0] or False,
            })
        return res

    def action_create_card(self, cr, uid, ids, context=None):
        for wz in self.browse(cr, uid, ids, context=context):
            datas = {
                'type': 'external',
                'internal_order_id': wz.internal_order_id and wz.internal_order_id.id or False,
                'liter': wz.liter or 0.0,
                'price_per_liter': wz.price_per_liter or 0.0,
                'amount': wz.amount or 0.0,
                'amount_ttc': wz.amount_ttc or 0.0,
                'driver_id': wz.driver_id and wz.driver_id.id or False,
                'owner': wz.owner or "", #and wz.owner_id.id or False,
                'manager': wz.manager or "", #and wz.manager_id.id or False,
                'vehicle_id': wz.vehicle_id and wz.vehicle_id.id or False,
                'vehicle_code': wz.vehicle_code or "",
                'gasoil_id': wz.gasoil_id and wz.gasoil_id.id or False,
                'vendor_id': wz.station_id and wz.station_id.id or False,
                'company_id': wz.company_id and wz.company_id.id or False,
                'date_order': wz.date_order or False,
                'date': wz.date or False,
                'inv_ref': wz.inv_ref or "",
                'tax_ids': [(6,0,[tax.id for tax in wz.tax_ids])],
                'state': 'assigned',
                }
            #print "\n datas", datas
            external_order_id = self.pool.get('fleet.vehicle.log.fuel').create(cr, uid, datas)
            #print "\n external_order_id", external_order_id
            #self.pool.get('fleet.vehicle.log.fuel').write(cr, uid, external_order_id, {'state': 'assigned'})
        return {'type': 'ir.actions.act_window_close'}

    _columns = {
        'liter': fields.float('Litrage (externe)', required=True), 
        'internal_order_id': fields.many2one('fleet.vehicle.log.fuel', 'Bon interne', required=True, readonly=True, help="Bon de carburant interne lié."),
        'price_per_liter' : fields.float('Prix au litre', required=True, digits_compute= dp.get_precision('Prix carburant')),
        'amount': fields.float('Montant HT', required=True, digits_compute= dp.get_precision('Montant carburant')),
        'amount_ttc': fields.float('Montant TTC', required=True, digits_compute= dp.get_precision('Montant carburant')),
        'driver_id': fields.many2one('hr.employee', 'Chauffeur', required=True, readonly=True),
        'vehicle_id': fields.many2one('fleet.vehicle', 'Véhicule', required=True, readonly=True),   
        'vehicle_code': fields.char('Référence véhicule', size=50, readonly=True),
        #'trailer': fields.many2one('tms.truck.trailer','semi-remorque'),    
        'gasoil_id': fields.many2one('product.product', 'Gasoil', required=True, domain=[('gasoil_ok','=',True)]),    
        'date_order': fields.datetime('Date du bon', required=True), 
        'station_id': fields.many2one('res.partner', 'Station/Fournisseur', required=True, domain=[('supplier','=',True)]),
        'company_id': fields.many2one('res.company', 'Société', required=True),
        'tax_ids': fields.many2many('account.tax', 'fuel_external_card_tax', 'card_id', 'tax_id', 'Taxes'),
        'inv_ref': fields.char('Référence facture', size=64),
        'date': fields.date('Date facture'),
        'owner': fields.char('Propriétaire', size=32, readonly=True),
        'manager': fields.char('Exploitant', size=32, readonly=True),
    }
    
    _defaults = {
        #'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'liter': lambda *a: 1.0,
        'price_per_liter': lambda *a: 0.0,
        'amount': lambda *a: 0.0,
        'amount_ttc': lambda *a: 0.0,
        }

    def onchange_gasoil_id(self, cr, uid, ids, prod_id=False, station_id=False, product_qty=0):
        price=0
        warning = {}
        result={}
        if not prod_id:
            return {}
        lang = False
        if not station_id:
            raise osv.except_osv('Fournisseur non défini !', 'Prière de selectionner un fournisseur pour l\'encodage du bon externe.')
        partner_id=self.pool.get('res.partner').browse(cr,uid,station_id)
        #if len(partner_id.address) == 0:
        #    raise osv.except_osv('Addresse fournisseur non définie !', 'Prière de selectionner un fournisseur avec une addresse.')
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
                                'title': 'Carburant sans prix !',
                                'message': 'Ce carburant ne possède pas de prix standard et n\'est lié à aucune liste de prix de ce fournisseur.',
                                }
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
        elif amount > 0 and liter > 0 and round(amount/liter,price_prec) != price_per_liter:
            return {'value' : {'price_per_liter' : round(amount / liter,price_prec),}}
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
        elif amount > 0 and liter > 0 and round(amount/liter,price_prec) != price_per_liter:
            return {'value' : {'price_per_liter' : round(amount / liter,price_prec),}}
        else :
            return {}

    def on_change_amount(self, cr, uid, ids, liter, price_per_liter, amount, amount_ttc, tax_ids, context=None):
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
        tax_list = [tax[2][0] for tax in tax_ids if tax[2]]
        price_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Prix carburant')
        amount_prec = self.pool.get('decimal.precision').precision_get(cr, uid, 'Montant carburant')
        new_price_per_liter = liter and round(amount / liter, price_prec) or 0.0
        new_liter = price_per_liter and round(amount/new_price_per_liter, 2) or 0.0
        if tax_list and amount > 0 and price_per_liter > 0 and liter > 0 :
            taxes = tax_obj.compute_all(cr, uid, tax_obj.browse(cr, uid, tax_list, context=context), new_price_per_liter, new_liter)
            #print "\n taxes", taxes
            if amount_ttc != taxes['total_included']:
                value = {'amount_ttc': taxes['total_included'],}
        if amount > 0 and liter > 0 and new_price_per_liter != price_per_liter:
            value.update({'price_per_liter': new_price_per_liter,})
            return {'value': value}
        elif amount > 0 and price_per_liter > 0 and new_liter != liter:
            value.update({'liter': new_liter,})
            return {'value': value}
        elif liter > 0 and price_per_liter > 0 and round(liter*price_per_liter,amount_prec) != amount:
            value.update({'amount': round(liter * price_per_liter,amount_prec),})
            return {'value': value}
        else :
            return {'value': value}


log_fuel_external_card()
