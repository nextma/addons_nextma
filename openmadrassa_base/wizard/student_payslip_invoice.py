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
from openerp import workflow

class account_voucher_validate(osv.osv):
    _name ="account.voucher.validate"

    def proforma_voucher(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [])
        for active_id in active_ids:
            workflow.trg_validate(uid, 'account.voucher', active_id, 'proforma_voucher', cr)
        return True


class account_invoice_cancel(osv.osv_memory):

    _name = "account.invoice.cancel"

    def invoice_cancel(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [])
        for active_id in active_ids:
            workflow.trg_validate(uid, 'account.invoice', active_id, 'invoice_cancel', cr)
        return True

class account_invoice_draft(osv.osv_memory):

    _name = "account.invoice.draft"

    def invoice_draft(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [])
        for invoice in self.pool['account.invoice'].browse(cr,uid,active_ids,context=context):
            invoice.action_cancel_draft()
        return True

class student_payslip_invoice(osv.osv_memory):

    _name = "student.payslip.invoice"
    _columns = {
        'journal_id': fields.many2one('account.journal', 'Destination Journal'),
    }
    _defaults = {

    }

    def view_init(self, cr, uid, fields_list, context=None):
        action_id = context.get('params').get('action')
        action_pool = self.pool['ir.actions.act_window']
        action = action_pool.read(cr, uid, action_id, context=context)
        name = "unknown"
        if action['view_id']:
            (view_id,name) = action['view_id']
        if context is None:
            context = {}
        res = super(student_payslip_invoice, self).view_init(cr, uid, fields_list, context=context)
        payslip_obj = self.pool.get('student.payslip')
        count = 0
        active_ids = context.get('active_ids',[])
        for payslip in payslip_obj.browse(cr, uid, active_ids, context=context):
            if payslip.invoice_state == "invoiced":
                count += 1
        if len(active_ids) == count and name != 'student.payslip.invoice.form2':
            raise osv.except_osv(_('Alert!'), _('Tous les éléments sélectionnés sont déjà facturés.'))
        return res

    def open_invoice(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        
        invoice_ids = self.create_invoice(cr, uid, ids, context=context)
        if not invoice_ids:
            raise osv.except_osv(_('Error!'), _("Aucune facture n'est créée!"))

        action = {}
        
        inv_type = 'out_invoice'
        data_pool = self.pool.get('ir.model.data')
        if inv_type == "out_invoice":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree1')
        elif inv_type == "in_invoice":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree2')
        elif inv_type == "out_refund":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree3')
        elif inv_type == "in_refund":
            action_id = data_pool.xmlid_to_res_id(cr, uid, 'account.action_invoice_tree4')

        if action_id:
            action_pool = self.pool['ir.actions.act_window']
            action = action_pool.read(cr, uid, action_id, context=context)
            action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
            return action
        return True

    def payslip_billable(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [])
        print context.get('active_model')
        if context.get('active_model') == 'student.payslip':
            self.pool['student.payslip'].write(cr,uid,active_ids,{'invoice_state':'2binvoiced'})
        return True

    def create_invoice(self, cr, uid, ids, context=None):
        context = dict(context or {})
        payslip_pool = self.pool.get('student.payslip')
        """
        data = self.browse(cr, uid, ids[0], context=context)
        journal2type = {'sale':'out_invoice', 'purchase':'in_invoice', 'sale_refund':'out_refund', 'purchase_refund':'in_refund'}
        context['date_inv'] = data.invoice_date
        acc_journal = self.pool.get("account.journal")
        inv_type = journal2type.get(data.journal_type) or 'out_invoice'
        context['inv_type'] = inv_type
        """
        tobinvoiced_active_ids = []
        active_ids = context.get('active_ids', [])
        for payslip in payslip_pool.browse(cr,uid,active_ids):
            if payslip.invoice_state != 'invoiced':
                tobinvoiced_active_ids.append(payslip.id)
        res = payslip_pool.create_invoice(cr,uid,tobinvoiced_active_ids,context=context)
        return res

class student_payslip_confirm(osv.osv_memory):

    _name = "student.payslip.confirm"

    def payslip_confirm(self, cr, uid, ids, context=None):
        active_ids = context.get('active_ids', [])
        for payslip in self.pool['student.payslip'].browse(cr,uid,active_ids):
            payslip.payslip_confirm()
        return True

