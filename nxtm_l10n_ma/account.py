# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2014 OpenERP S.A. (<http://openerp.com>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Frddee Software Foundation, either version 3 of the
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
from openerp.osv import osv


# ---------------------------------------------------------
# Account generation from template wizards
# ---------------------------------------------------------
class wizard_multi_charts_accounts(osv.osv_memory):
    """
    Create a new account chart for a company.
    Wizards ask for:
        * a company
        * an account chart template
        * a number of digits for formatting code of non-view accounts
        * a list of bank accounts owned by the company
    Then, the wizard:
        * generates all accounts from the template and assigns them to the right company
        * generates all taxes and tax codes, changing account assignations
        * generates all accounting properties and assigns them correctly
    """
    _inherit='wizard.multi.charts.accounts'


    def execute(self, cr, uid, ids, context=None):
        '''
        This function is called at the confirmation of the wizard to generate the COA from the templates. It will read
        all the provided information to create the accounts, the banks, the journals, the taxes, the tax codes, the
        accounting properties... accordingly for the chosen company.
        '''
        result = super(wizard_multi_charts_accounts,self).execute(cr, uid,ids,context=context)
        self.update_data(cr,uid,ids,context=context)
        return result

    def update_data(self, cr, uid,ids, context=None):

        journal_obj = self.pool.get('account.journal')
        account_obj = self.pool.get('account.account')
        property_obj = self.pool.get('ir.property')
                
        journal_bank_id = journal_obj.search(cr,uid,[('code','=','BNK2'),('type','=','bank')], context=context)
        account_journal_bank_id = account_obj.search(cr,uid,[('code','=','514100')], context=context)

        journal_cash_id = journal_obj.search(cr,uid,[('code','=','BNK1'),('type','=','cash')], context=context)
        account_journal_cash_id = account_obj.search(cr,uid,[('code','=','516110')], context=context)

        journal_purchase_id = journal_obj.search(cr,uid,[('code','=','EXJ'),('type','=','purchase')], context=context)
        account_journal_purchase_id = account_obj.search(cr,uid,[('code','=','611100')], context=context)
        journal_purchase_refund_id = journal_obj.search(cr,uid,[('code','=','ECNJ'),('type','=','purchase_refund')], context=context)

        journal_sale_id = journal_obj.search(cr,uid,[('code','=','SAJ'),('type','=','sale')], context=context)
        journal_sale_refund_id = journal_obj.search(cr,uid,[('code','=','SCNJ'),('type','=','sale_refund')], context=context)

        property_id = property_obj.search(cr,uid,[('name','=',('property_account_expense_categ'))], context=context)
        property_account_id = account_obj.search(cr,uid,[('code','=','611100')], context=context)

        journal_situation_id = journal_obj.search(cr,uid,[('code','=','AN'),('type','=','situation')], context=context)
        account_journal_situation_id = account_obj.search(cr,uid,[('code','=','8600')], context=context)

        print journal_situation_id
        if journal_bank_id and account_journal_bank_id:
            journal_obj.write(cr,uid,journal_bank_id[0],{'default_debit_account_id':account_journal_bank_id[0],'default_credit_account_id':account_journal_bank_id[0]})

        if journal_bank_id:
            journal_obj.write(cr,uid,journal_bank_id[0],{'code':'BNK'})

        if journal_cash_id and account_journal_cash_id:
            journal_obj.write(cr,uid,journal_cash_id[0],{'default_debit_account_id':account_journal_cash_id[0],'default_credit_account_id':account_journal_cash_id[0]})

        if journal_cash_id:
            journal_obj.write(cr,uid,journal_cash_id[0],{'code':'CAISS','name':'CAISSE'})

        if journal_purchase_id and account_journal_purchase_id:
            journal_obj.write(cr,uid,journal_purchase_id[0],{'default_debit_account_id':account_journal_purchase_id[0],'default_credit_account_id':False})
        if journal_purchase_id:
            journal_obj.write(cr,uid,journal_purchase_id[0],{'code':'ACHT'})
        
        if journal_purchase_refund_id and account_journal_purchase_id:
            journal_obj.write(cr,uid,journal_purchase_refund_id[0],{'default_debit_account_id':False,'default_credit_account_id':account_journal_purchase_id[0]})
        if journal_purchase_refund_id:
            journal_obj.write(cr,uid,journal_purchase_refund_id[0],{'code':'AVACH'})
        
        if journal_sale_id:
            journal_obj.write(cr,uid,journal_sale_id[0],{'code':'JVT','default_debit_account_id':False})

        if journal_sale_refund_id:
            journal_obj.write(cr,uid,journal_sale_refund_id[0],{'code':'AVVT','default_credit_account_id':False})

        if property_id and property_account_id:
            property_obj.write(cr,uid,property_id[0],{'value_reference':'account.account,'+str(property_account_id[0])})

        if journal_situation_id and account_journal_situation_id:
            journal_obj.write(cr,uid,journal_situation_id[0],{'default_debit_account_id':account_journal_situation_id[0],'default_credit_account_id':account_journal_situation_id[0]})

                
        return True





# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
