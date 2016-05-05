# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
from openerp import fields, api, models, _,workflow
from openerp.addons.account.account_invoice import TYPE2JOURNAL
from openerp.exceptions import Warning
from openerp.osv import osv

compteur = 0

class student_fees_structure(models.Model):
    '''
    Student Fees Structure
    '''
    _inherit = 'student.fees.structure'
    


    def unlink(self, cr, uid, ids, context=None):
        structure_line_ids = self.pool['student.payslip'].search(cr,uid,[('register_id','=',ids[0])])
        if not structure_line_ids:
            return osv.osv.unlink(self, cr, uid, ids, context=context)
            

class student_fees_structure_line(models.Model):
    '''
    Student Fees Structure Line
    '''
    _inherit = 'student.fees.structure.line'
    
    #name = fields.Many2one('product.product',string='Article')
    name = fields.Char(compute='_compute_name',string='Article')
    product_id = fields.Many2one('product.product',string='Name')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        for line in self:
            line.amount = line.product_id.lst_price
        
    def _compute_name(self):
        for line in self:
            line.name = line.product_id.name

class student_payslip_line(models.Model):
    _inherit = 'student.payslip.line'
    
    #name = fields.Many2one('product.product',string='Article',required=True)
    name = fields.Char(compute='_compute_name',string='Name',required=True)
    product_id = fields.Many2one('product.product',string='Name',required=True)

    @api.onchange('product_id')
    def onchange_product_id(self):
        for line in self:
            line.amount = line.product_id.lst_price

    def _compute_name(self):
        for line in self:
            line.name = line.product_id.name


class student_fees_register(models.Model):
    """
    Student fees Register
    """
    _inherit = 'student.fees.register'

    company_id = fields.Many2one('res.company', 'Company', required=True, change_default=True, readonly=True, states={'draft':[('readonly', False)]},default=lambda self: self.env['res.users'].browse([self._uid])[0].company_id.id)

    @api.multi
    def fees_register_confirm(self):
        for register in self:
            payslips = register.line_ids
            for payslip in payslips:
                workflow.trg_validate(self._uid, 'student.payslip', payslip.id, 'payslip_confirm', self._cr)

            amount = 0
            for line in register.line_ids:
                amount = amount + line.total
            register.total_amount = amount
            register.write({'state' : 'confirm'})
        return True

class student_payslip(models.Model):


    def unlink(self, cr, uid, ids, context=None):
        for payslip in self.browse(cr,uid,ids):
            if payslip.state != 'draft':
                raise Warning(_('Vous ne pouvez pas supprimer une réception de frais déjà validée.')) 
        payslip_line_obj = self.pool['student.payslip.line']
        payslip_line_ids = payslip_line_obj.search(cr,uid,[('slip_id','=',ids[0])])
        res = osv.osv.unlink(self, cr, uid, ids, context=context)
        if payslip_line_ids:
            payslip_line_obj.unlink(cr,uid,payslip_line_ids)
        invoice_obj = self.pool['account.invoice']
        invoice_ids =  invoice_obj.search(cr,uid,[('fees_id','in',ids)])
        for invoice in invoice_obj.browse(cr,uid,invoice_ids):
            invoice.state = 'cancel'
        return res

    
    def create(self,cr,uid,vals,context=None):
        id = super(student_payslip,self).create(cr,uid,vals,context=context)
        payslip = self.browse(cr,uid,id)
        payslip.payslip_line()
        return id

    @api.returns('self', lambda value:value.id)
    def copy(self, cr, uid, id, default=None, context=None):
        data = self.browse(cr,uid,id)
        default.update({'invoice_state':'2binvoiced','state':'draft'})
        if data.name:
            default.update({'name':data.name+' copie'})
        return models.Model.copy(self, cr, uid, id, default=default, context=context)

    @api.multi
    def payslip_line(self):

        def get_price(self,product_id,structure_amount):
            for line in self.student_id.pricelist_ids:
                if  line.fees_struct_line_id.product_id.id == product_id: 
                    return line.amount
            return structure_amount
        
        student_payslip_line_obj = self.env['student.payslip.line']
        for student_payslip_datas in self:
            student_fees_structure_search_ids = student_payslip_datas.fees_structure_id

            for datas in student_fees_structure_search_ids:
                for data in datas.line_ids or []:
                    student_payslip_line_vals = {
                                                 'slip_id':self.id,
                                                 'product_id':data.product_id.id,
                                                 'code':data.code,
                                                 'type':data.type,
                                                 'amount':get_price(self,data.product_id.id,data.amount),
                            }
                    print student_payslip_line_vals
                    student_payslip_line_obj.create(student_payslip_line_vals)
            amount = 0
            for datas in self.browse(self.ids):
                for data in datas.line_ids:
                    amount = amount + data.amount
                student_payslip_vals = {'total':amount}
                datas.write(student_payslip_vals)
        return True

    @api.multi
    def payslip_confirm(self):
        for student_payslip_datas in self:
            if not student_payslip_datas.fees_structure_id:
                self.write({'state' : 'paid'})   
                return True
        self.create_invoice()
        self.write({'state' : 'confirm'})
        return True


    def action_view_invoice(self, cr, uid, ids, context=None):
        '''
        This function returns an action that display existing invoices of given sales order ids. It can either be a in a list or in a form view, if there is only one invoice to show.
        '''
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')

        result = mod_obj.get_object_reference(cr, uid, 'account', 'action_invoice_tree1')
        id = result and result[1] or False
        result = act_obj.read(cr, uid, [id], context=context)[0]
        #compute the number of invoices to display
        inv_ids = self.pool['account.invoice'].search(cr,uid,[('fees_id','in',ids)])
        #choose the view_mode accordingly
        if len(inv_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, inv_ids))+"])]"
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = inv_ids and inv_ids[0] or False
        return result

    def student_pay_fees(self, cr, uid, ids, context=None):
        """Creates student related account voucher
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : new form of account.voucher model
        """

        if not ids: return []
        fees = self.browse(cr, uid, ids[0], context=context)
        return {
        'name':_("Pay Fees"),
            'view_mode': 'form',
            'view_id': False,
            'view_type': 'form',
            'res_model': 'account.voucher',
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'domain': '[]',
            'context': {
                'default_fees_id' : fees.id,
                'default_partner_id': fees.student_id.partner_id.parent_id.id or fees.student_id.partner_id.id,
                'default_amount': fees.balance,
                'default_name':fees.name,
                'default_date' : fees.date,
                'close_after_process': True,
                'invoice_type': 'out_invoice',
                'default_type': 'receipt',
                'type': 'receipt'
            }
        }

    """
    def _compute_payments_OLD(self):
        for fees in self:
            invoice_ids = self.env['account.invoice'].search([('fees_id','=',fees.id)])
            lines = self.env['account.move.line']
            for invoice in invoice_ids:
                lines |= invoice.payment_ids
            fees.payment_ids = lines.sorted()
    """

    @api.one
    @api.depends(
        'voucher_id',
        'voucher_id.move_ids',
    )

    def _compute_payments(self):
        lines = self.env['account.move.line']
        for line in self.voucher_id.move_ids:
            if line.account_id != self.student_id.partner_id.property_account_receivable:
                continue
            
            lines |= line
        self.payment_ids = lines.sorted()
        self._get_amount_paid()
        self._get_balance()
            


    @api.one
    @api.depends(
        'total',
        'paid_amount',
    )    
    def _get_balance(self):
        balance = self.total - self.paid_amount
        if balance <= 0:
            self.state = "paid"
        else :
            self.state = 'confirm'
        self.balance = balance

    @api.one
    @api.depends(
        'payment_ids',
    )    
    def _get_amount_paid(self):
        paid_amount = 0.0
        for payment in self.payment_ids:
            paid_amount += payment.credit
        self.paid_amount = paid_amount
        
    """
    def _get_amount_paid_OLD(self):
        for fees in self:
            amount = 0.0
            for line in fees.payment_ids:
                amount += line.credit
            fees.paid_amount = amount
    """

    @api.model
    def _default_journal(self):
        inv_type = self._context.get('type', 'out_invoice')
        inv_types = inv_type if isinstance(inv_type, list) else [inv_type]
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        domain = [
            ('type', 'in', filter(None, map(TYPE2JOURNAL.get, inv_types))),
            ('company_id', '=', company_id),
        ]
        return self.env['account.journal'].search(domain, limit=1)

    def _company_default_get(self):
        company_id = self._context.get('company_id', self.env.user.company_id.id)
        return company_id

    def _get_default_period(self):
        period_obj = self.env['account.period']
        period_id = period_obj.find(dt=None)
        return period_id and period_id[0].id

    _inherit = 'student.payslip'

    journal_id = fields.Many2one('account.journal', string='Journal',
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_default_journal,
        domain="[('type', 'in', {'out_invoice': ['sale'], 'out_refund': ['sale_refund'], 'in_refund': ['purchase_refund'], 'in_invoice': ['purchase']}.get(type, [])), ('company_id', '=', company_id)]")
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, readonly=True, states={'draft': [('readonly', False)]},
        default=_company_default_get)
    period_id = fields.Many2one('account.period', 'Force Period', required=True,default=_get_default_period, domain=[('state', '<>', 'done')], help="Keep empty to use the period of the validation(invoice) date.")
    payment_ids = fields.Many2many('account.move.line', string='Payments',
        compute='_compute_payments')
    paid_amount = fields.Float(string='Total paiements reçus',compute='_get_amount_paid',store=True)
    #paid_amount = fields.Float(string='Total paiements reçus')
    balance = fields.Float(string='Reste à payer',compute='_get_balance',store=True)
    invoice_state = fields.Selection([('2binvoiced','À facturer'),('invoiced','Facturé')],string='Facturation',default='2binvoiced')
    partner_id = fields.Many2one('res.partner',string='Parent',domain="[('parent_id','=',False)]")
    invoice_id = fields.Many2one('account.invoice',string='Facture')
    voucher_id = fields.Many2one('account.voucher','Payement')
    
    def create_invoice(self,cr,uid,ids,context=None):
        invoice_ids = []
        for rec in self.browse(cr,uid,ids):
            invoice_data = {
                            #'partner_id' : rec.student_id.partner_id.parent_id.id or rec.student_id.partner_id.id,
                             'partner_id' : rec.student_id.partner_id.id,
                            'journal_id' : rec.journal_id.id,
                            'period_id' : rec.period_id.id,
                            'date_invoice' : rec.date,
                            'account_id' : rec.student_id.partner_id.property_account_receivable.id,
                            'fees_id' : rec.id,
                            }
            
            invoice_id  = self.pool['account.invoice'].create(cr,uid,invoice_data)
            invoice_ids.append(invoice_id)
            for line in rec.line_ids:
                invoice_line_data = {
                                     'product_id' : line.product_id.id,
                                     'name' : line.product_id.name,
                                     'account_id': line.product_id.property_account_income.id or line.product_id.categ_id.property_account_income_categ.id,
                                     'quantity' : 1.0,
                                     'price_unit' : line.amount,
                                     'invoice_line_tax_id' :[],
                                     'invoice_id' : invoice_id,
                                     }
                self.pool['account.invoice.line'].create(cr,uid,invoice_line_data)
            rec.invoice_state = 'invoiced'
            rec.invoice_id = invoice_id
            workflow.trg_validate(uid, 'account.invoice', invoice_id, 'invoice_open', cr)
        return invoice_ids
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
