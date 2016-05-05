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
import time

from openerp import api
from openerp.osv import fields, osv


class account_account(osv.osv):
    _inherit ="account.account"
    _columns = {
            'code_stu' : fields.char('Stu'),
        }

    
class account_voucher(osv.osv):

    def proforma_voucher(self, cr, uid, ids, context=None):
        payslip_obj  = self.pool.get('student.payslip')
        back = super(account_voucher,self).proforma_voucher(cr,uid,ids,context=context)
        vouchers = self.browse(cr,uid,ids,context=context)
        fees_ids = []
        for voucher in vouchers:
            for line in voucher.line_cr_ids:
                slip_id  = line.move_line_id.invoice.fees_id.id
                if slip_id:
                    payslip_obj.write(cr,uid,slip_id,{'voucher_id':voucher.id})
                    fees_ids.append(slip_id)
        fees_ids = set(fees_ids)
        if fees_ids:
            for fees_id in fees_ids:
                payslip_obj.browse(cr,uid,fees_id)._compute_payments()
        return back

    def compute_all(self,cr,uid,ids,context=None):
        domain = [('state','=','draft')]
        voucher_ids = self.search(cr,uid,domain)
        voucher = self.browse(cr,uid,voucher_ids,context=context)
        for v in voucher:
            print v.name
            self.proforma_voucher(cr, uid, v.id, context=context)


    
    _inherit = 'account.voucher'
    
    
    
    def create(self,cr,uid,vals,context=None):
        voucher_line_pool = self.pool['account.voucher.line']
        voucher_id  = super(account_voucher,self).create(cr,uid,vals,context=context)
        voucher = self.browse(cr,uid,voucher_id)
        default = voucher.onchange_journal_voucher([l.id for l in voucher.line_ids], voucher.tax_id.id, voucher.amount, voucher.partner_id.id, voucher.journal_id.id, voucher.type, voucher.company_id.id, context=context)
        if context and context.get('install_mode'):
            values = default.get('value').get('line_cr_ids')
            for value in values:
                """
                if value.get('date_original') == str(voucher.date):
                    value['reconcile'] = True
                """
                value['voucher_id'] = voucher_id
                voucher_line_pool.create(cr,uid,value)
        return voucher_id

    """Permettre l'exécution de la méthode onchange_amount autrement"""
    def write(self,cr,uid,ids,vals,context=None):
        if context and context.get('install_mode'):
            print "##################################"
            if "amount" in vals:
                print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
                for voucher in self.browse(cr,uid,ids):
                    line_to_update = voucher.line_cr_ids and voucher.line_cr_ids[0] or False
                    if line_to_update:
                        diff = vals.get('amount')-line_to_update.amount_unreconciled
                        if diff >=0:
                            amount_line = line_to_update.amount_unreconciled
                            line_to_update.reconcile = True
                        else :
                            amount_line = vals.get('amount')
                            line_to_update.reconcile = False
                        line_to_update.amount = amount_line
                        print "*************************************"
        return super(account_voucher,self).write(cr,uid,ids,vals,context=context)

class account_voucher_line(osv.osv):
    _inherit = 'account.voucher.line'


    _columns = {
        #'date_original': fields.related('move_line_id','date', type='date', relation='account.move.line', string='Date', readonly=1,store=True),
    }

class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _columns = {
            'fees_id' : fields.many2one('student.payslip','Frais associé'),
        }


# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
