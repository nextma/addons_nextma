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
from openerp.osv import osv,fields

class hr_employee(osv.osv):
    _inherit = "hr.employee"
    _columns = {
        'job': fields.char('Nom job'),
        'bank_code_temp': fields.char('Banque code'),
        }

    def createe(self,cr,uid,vals,context=None):
        print vals.get('bank_code_temp')
        if vals.get('job'):
            job_id = self.pool['hr.job'].search(cr,uid,[('name','=',vals.get('job'))])
        if (vals.get('job')) and (not job_id):
            job_id = [self.pool['hr.job'].create(cr,uid,{'name':vals.get('job')}) ]
        if vals.get('bank_code_temp'):
            bank_id = self.pool['res.partner.bank'].search(cr,uid,[('acc_number','=',vals.get('bank_code_temp'))])
        if vals.get('bank_code_temp') and (not bank_id):
            bank_id = [self.pool['res.partner.bank'].create(cr,uid,{'acc_number':vals.get('bank_code_temp'),'state':'bank'}) ]
        if vals.get('job') :
            vals['job_id'] = job_id[0]
        if vals.get('bank_code_temp'):
            vals['bank_account_id'] = bank_id[0]
        address_id = self.pool['res.partner'].search(cr,uid,[('name','=',vals.get('name'))])
        if address_id:
            vals['address_home_id'] = address_id[0]
            vals['address_id'] = address_id[0]
        return super(hr_employee,self).create(cr,uid,vals,context=context)