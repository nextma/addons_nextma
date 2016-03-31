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

from openerp import api
from openerp.osv import fields, osv
from openerp.tools.translate import _


class picking_make_invoice(osv.osv_memory):
    _name = "picking.make.invoice"
    _description = "Pickings Make Invoice"

    _columns = {
        'grouped': fields.boolean('Grouper par Client', help='Check the box to group the invoices for the same customers'),
        'grouped_by_product' : fields.selection([('travel_and_type','Grouper les BLs par voyage et par type de transport'),('travel_and_vehicle','Grouper les BLs par voyage et par véhicule')],'Options supplémentaires',help='Check the box to group the invoices according to the choice'),
        'invoice_date': fields.date('Invoice Date'),
    }
    _defaults = {
        'grouped': False,
        #'invoice_date': fields.date.context_today,
    }
    @api.multi
    def onchange_grouped(self,grouped):
        if grouped == False :
            return {'value':{'grouped_by_product':False}}

    @api.multi
    def onchange_grouped_by_product(self,grouped_by_product):
        if grouped_by_product:
            return {'value':{'grouped':True}}
        
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        picking = self.pool.get('tms.picking').browse(cr, uid, record_id, context=context)
        if picking.state != 'done':
            raise osv.except_osv(_('Warning!'), _('You cannot create invoice when picking is not confirmed.'))
        return False

    def make_invoices2(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('tms.picking')
        #mod_obj = self.pool.get('ir.model.data')
        #act_obj = self.pool.get('ir.actions.act_window')
        account_obj = self.pool.get('account.journal')
        journal_id = account_obj.search(cr,uid,[('type','=','out_invoice')])
        journal = account_obj.browse(cr,uid,journal_id)
        #newinv = []
        context = context or {}
        todo = {}
        data = self.browse(cr,uid,ids[0],context=context)
        active_ids = context.get('active_ids', [])
        context.update({'grouped_by_product':data.grouped_by_product})
        context.update({'date_inv':data.invoice_date})
        for picking in picking_obj.browse(cr,uid,active_ids,context=context):
            if data['grouped'] :
                if picking.partner_invoiced_id :
                    key = picking.partner_invoiced_id.id
                    if not context.get('partner_delivery_id') :
                        context.update({'partner_delivery_id':picking.partner_id.id})
                else :
                    key = picking.partner_id.id
            else :
                key = picking.id
            if picking.state == 'done':
                todo.setdefault(key, [])
                todo[key].append(picking)
        invoices = []
        inv_type = 'out_invoice'
        for moves in todo.values():
            invoices += picking_obj._invoice_create_line(cr, uid, moves,journal,inv_type,context=context)
        
        return  invoices
    
    def make_invoices(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('tms.picking')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        newinv = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        data1= self.read(cr, uid, ids)
        print '===================='
        print data1
        print picking_obj
        record_id = context and context.get('active_id', False)
        records =context.get('active_ids', False)
        if data['grouped'] == False:
            print '@@@@@@@@@@@@@@false'
            for record in records:
                picking = self.pool.get('tms.picking').browse(cr, uid, record, context=context)
                invoice_id=self.pool.get('tms.picking').action_invoice_create(cr, uid,record,picking.tax_ids,picking.product_uom_id.id,picking.product_id.name,picking.product_id.id,picking.product_qty,picking.price_unit,picking.partner_id.id,date_invoice=data['invoice_date'], context=context)
                self.pool.get('tms.picking').write(cr, uid, record,{'invoice_state': 'invoiced'},context=context)
                print '-----------------------'
                print picking.invoice_id
                self.pool.get('tms.picking').write(cr, uid, record,{'invoice_id': invoice_id},context=context)
            picking.invoice_id=invoice_id
            self.pool.get('account.invoice').button_compute(cr, uid, [invoice_id])
        else :
            print '@@@@@@@@@@@@@@true'
            partner_id=''
            for record in records:
                picking = self.pool.get('tms.picking').browse(cr, uid, record, context=context)
                partner_id=picking.partner_id.id
            invoice_id=self.pool.get('tms.picking').create_invoice(cr, uid, ids,partner_id,date_invoice=data['invoice_date'], context=context)
            picking.invoice_id=invoice_id
            for record in records:
                picking = self.pool.get('tms.picking').browse(cr, uid, record, context=context)
                self.pool.get('tms.picking').write(cr, uid, record,{'invoice_state': 'invoiced'},context=context)
                self.pool.get('tms.picking').write(cr, uid, record,{'invoice_id': invoice_id},context=context)
                print '-----------------------'
                print picking.invoice_id
                invoice_lines = self.pool.get('account.invoice.line').search(cr, uid, [('invoice_id','=',invoice_id)])                
                print '@@@@@@@@@@@@@@@@@@@@Invoice lines@@@@@@@@@@@@@@@@@@@@@@@'
                print invoice_lines
                company_id=self.pool['res.company']._company_default_get(cr,uid,object='tms_picking',context=context)
                invoice_specs=self.pool.get('tms.picking').get_partner_account_id(cr,uid,ids,partner_id,company_id)
                invoice_line_spec=self.pool.get('tms.picking').get_product_account_id(cr, uid, ids,picking.product_id.id,'out_invoice', partner_id, False,context, company_id)
                print '||||||||||||||||||||'
                print invoice_line_spec['account_id']
                print 'taxe'
                print picking.tax_ids

                invoice_line_id = self.pool.get('account.invoice.line').create(cr,uid,{
                         'invoice_id':invoice_id,
                         'name':picking.product_id.name,
                         'account_id':invoice_line_spec['account_id'],
                         'product_id':picking.product_id.id,
                         'price_unit':picking.price_unit,
                         'quantity':picking.product_qty,
                         'uos_id':picking.product_uom_id.id,
                         'invoice_line_tax_id':[(6, 0, [x.id for x in picking.tax_ids])],
                      }, context=context)

                for invoice_line in invoice_lines:
                    invoice_line_record = self.pool.get('account.invoice.line').browse(cr, uid, invoice_line, context=context)
                    print invoice_line_record.product_id.id
                    print picking.product_id.id
                    if(invoice_line_record.product_id.id == picking.product_id.id):
                        print 'same products'
                        print 'quantity'
                        print invoice_line_record.quantity
                        print 'new quantity'
                        new_quantity=invoice_line_record.quantity+picking.product_qty
                        price_unit=picking.price_unit
                        print new_quantity
                        self.pool.get('account.invoice.line').write(cr, uid, invoice_line_record.id, {'quantity': new_quantity,'price_unit':price_unit}, context=context)
                        self.pool.get('account.invoice.line').unlink(cr, uid,invoice_line_id, context=context)
                    else:
                        print 'different products'
                self.pool.get('account.invoice').button_compute(cr, uid, [invoice_id])
        for o in picking_obj.browse(cr, uid, context.get(('active_ids'), []), context=context):
            newinv.append(o.invoice_id.id)
            

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        result['domain'] = "[('id','in', [" + ','.join(map(str, newinv)) + "])]"
        result={}
        return  {'value': result}

picking_make_invoice()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
