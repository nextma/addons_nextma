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
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import api
from datetime import date

class student_monthly_fees(osv.TransientModel):
    """
    Générateur des frais mensuels
    """
    
    def _get_default_period(self,cr,uid,ids,context=None):
        period_obj = self.pool['account.period']
        period_id = period_obj.search(cr,uid,[('date_start','<=',date.today()),('date_stop','>=',date.today())])
        return period_id and period_id[0]

    def _get_default_journal(self,cr,uid,ids,context=None):
        journal_obj = self.pool['account.journal']
        journal_id = journal_obj.search(cr,uid,[('type','=','sale')])
        return journal_id and journal_id[0]

    def _get_default_structure(self,cr,uid,ids,context=None):
        structure_obj = self.pool['student.fees.structure']
        structure_id = structure_obj.search(cr,uid,[(1,'=',1)])
        if len(structure_id)>1:
            return structure_id[1]
        return structure_id and structure_id[0]
    
    _name = "student.monthly.fees"
    _columns = {
        'student_fees_structure_id'  : fields.many2one('student.fees.structure','Structure de frais',required=True),
        'journal_id' : fields.many2one('account.journal','Journal',required=True),
        'period_id' : fields.many2one('account.period','Période de travail',required=True),
        'date' :  fields.date('Date',required=True),
        'student_all' : fields.boolean('Tous les étudiants',help="Décochez cette case si vous voulez générer les frais pour quelques étudiants seulement.Dans ce cas vous devez selectionner les étudiants"),
        'student_ids' : fields.many2many('student.student','monthly_fees_student_student','monthly_fees_id','student_id','Étudiants concernés'),
    }
    
    _defaults={
        'date' : date.today(),
        'period_id' : _get_default_period,
        'journal_id' :_get_default_journal,
        'student_fees_structure_id' :_get_default_structure,
        'student_all' : True,
    }

    @api.onchange('date')
    def onchange_date(self):
        period_obj = self.env['account.period']
        period_id = period_obj.search([('date_start','<=',self.date),('date_stop','>=',self.date)])
        print period_id.id
        if period_id:
            self.period_id = period_id.id

    def generate_fees(self, cr, uid, ids, context=None):
        ''' This method allows you to generate fees 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : record of monthly attendance sheet        
        '''
        
        fees_register_obj = self.pool['student.fees.register']
        student_obj = self.pool['student.student']
        student_payslip_obj = self.pool['student.payslip']
        
        data = self.browse(cr,uid,ids)
        name = 'frais '+data.period_id.name
        fees_register_id=fees_register_obj.create(cr,uid,{'name':name,'date':data.date,'period_id':data.period_id.id,'journal_id':data.journal_id.id})
        '''
          generation of fees line  per student
        '''
        if data.student_all:
            student_ids = student_obj.search(cr,uid,[])
            students = student_obj.browse(cr,uid,student_ids)
        else:
            students = data.student_ids
        for student in students : 
            payslip_data = {
                     'name' : name,
                     'date' : data.date,
                     'journal_id' : data.journal_id.id,
                     'period_id' :data.period_id.id,
                     'student_id' : student.id,
                     'partner_id' : student.partner_id.parent_id.id,
                     'standard_id' : student.standard_id.id,
                     'division_id': student.division_id.id,
                     'medium_id' :student.medium_id.id,
                     'fees_structure_id' : data.student_fees_structure_id.id,
                     'company_id' : student.company_id.id,
                     'register_id' : fees_register_id, 
                    }
            student_payslip_obj.create(cr,uid,payslip_data)
            #student_payslip_ids.append(student_payslip_id)
            

        """ Confirmation  de l'inscription """
        #fees_register_obj.write(cr,uid,fees_register_id,{'state' : 'confirm'})
        fees_register_obj.browse(cr,uid,fees_register_id).fees_register_confirm()
        
        #student_payslip_obj.create_invoice(cr,uid,student_payslip_ids)
            

        models_data = self.pool.get('ir.model.data')
        # Get opportunity views
        dummy, form_view = models_data.get_object_reference(cr, uid, 'school_fees', 'view_student_fees_register_form')
        dummy, tree_view = models_data.get_object_reference(cr, uid, 'school_fees', 'view_student_fees_register_tree')
        
        return {
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'student.fees.register',
            'view_id': False,
            'domain': [('id', '=', fees_register_id)],
            'views': [(tree_view or False, 'tree'),(form_view or False, 'form')],
            'type': 'ir.actions.act_window',
        }   


    def generate_fees_old(self, cr, uid, ids, context=None):
        ''' This method allows you to generate fees 
        @param self : Object Pointer
        @param cr : Database Cursor
        @param uid : Current Logged in User
        @param ids : Current Records
        @param context : standard Dictionary
        @return : record of monthly attendance sheet        
        '''
        
        fees_register_obj = self.pool['student.fees.register']
        student_obj = self.pool['student.student']
        student_payslip_obj = self.pool['student.payslip']
        student_fees_structure_obj = self.pool['student.fees.structure']
        
        data = self.browse(cr,uid,ids)
        name = 'frais '+data.period_id.name
        print data.period_id.name
        fees_register_id=fees_register_obj.create(cr,uid,{'name':name,'date':data.date,'period_id':data.period_id.id,'journal_id':data.journal_id.id})
        
        '''
          generation of fees line  per student
        '''
        student_ids = student_obj.search(cr,uid,[(1,'=',1)])
        students = student_obj.browse(cr,uid,student_ids)
        #student_fees_structure_id = student_fees_structure_obj.search(cr,uid,[(1,'=',1)])
        for student in students : 
            payslip_data = {
                     'name' : name,
                     'date' : data.date,
                     'journal_id' : data.journal_id.id,
                     'period_id' :data.period_id.id,
                     'student_id' : student.id,
                     'standard_id' : student.standard_id.id,
                     'division_id': student.division_id.id,
                     'medium_id' :student.medium_id.id,
                     'fees_structure_id' : data.student_fees_structure_id.id,
                     'company_id' : student.company_id.id,
                     'register_id' : fees_register_id, 
                    }
            student_payslip_id = student_payslip_obj.create(cr,uid,payslip_data)

        models_data = self.pool.get('ir.model.data')
        # Get opportunity views
        dummy, form_view = models_data.get_object_reference(cr, uid, 'school_fees', 'view_student_fees_register_form')
        dummy, tree_view = models_data.get_object_reference(cr, uid, 'school_fees', 'view_student_fees_register_tree')
        
        return {
            'view_type': 'form',
            'view_mode': 'tree, form',
            'res_model': 'student.fees.register',
            'view_id': False,
            'domain': [('id', '=', fees_register_id)],
            'views': [(tree_view or False, 'tree'),(form_view or False, 'form')],
            'type': 'ir.actions.act_window',
        }   
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
