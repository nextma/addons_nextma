# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

"""
class student_code(osv.osv):
	_name = "student.code"
	_columns = {
		'name' : fields.char('Nom complet'),
		'name_arab' : fields.char('Nom arabe'),
		'nom' : fields.char('Nom'),
		'prenom' : fields.char('Prenom'),
		'code' : fields.char('Code'),
		'standard_id':fields.many2one('standard.standard', 'Class'),
		'division_id':fields.many2one('standard.division', 'Division'),
		}
"""

import logging

from openerp import api
from openerp.osv import osv, fields


class school_standard(osv.Model):
	_inherit = 'school.standard'

	def _compute_student(self, cr, uid, ids, name, args, context=None):
		''' This function will automatically computes the students related to particular standard.'''
		result = {}
		student_obj = self.pool.get('student.student')
		for standard_data in self.browse(cr, uid, ids, context=context):
			#domain = [('standard_id', '=', standard_data.standard_id.id),('division_id','=',standard_data.division_id.id),('medium_id','=',standard_data.medium_id.id)]
			domain = [('standard_id', '=', standard_data.standard_id.id),('division_id','=',standard_data.division_id.id)]
			student_ids = student_obj.search(cr, uid,domain, context=context)
			result[standard_data.id] = student_ids
		return result
	
	def _student_search(self, cr, uid, obj, field_name, args, context=None):
		school_standard_ids = []
		student_obj = self.pool.get('student.student')
		school_standard_obj = self.pool.get('school.standard')
		for arg in args:
			(key,operator,values) = arg
			if key == "student_ids":
				for student in student_obj.browse(cr,uid,values):
					#domain = [('standard_id', '=', student.standard_id.id),('division_id','=',student.division_id.id),('medium_id','=',student.medium_id.id)]
					domain = [('standard_id', '=', student.standard_id.id),('division_id','=',student.division_id.id)]					
					school_standard_ids.extend(school_standard_obj.search(cr,uid,domain))
				break
		return [('id', 'in', school_standard_ids)]
	
	_columns = {
        'student_ids': fields.function(_compute_student,method=True,relation='student.student',fnct_search=_student_search, type="one2many",string='Student In Class'),
    	   	}
	
class academic_year(osv.Model):
	_inherit = "academic.year"

	@api.model
	@api.returns('self', lambda value:value.id)
	def create(self, vals):
		month_obj = self.env['academic.month']
		periods = self.env['account.period'].search([('date_start','>=',vals.get('date_start')),('date_stop','<=',vals.get('date_stop')),('special','=',False)])
		year = osv.Model.create(self, vals)
		for period in periods:
			datas ={
				'name' : period.name,
				'code' : period.code,
				'date_start' : period.date_start,
				'date_stop' : period.date_stop,
				'year_id' : year.id,
				}
			month_obj.create(datas)
		return year

class student_pricelist(osv.osv):
	_name = 'student.pricelist'
	
	_columns = {
		 'fees_struct_line_id' : fields.many2one('student.fees.structure.line','Ligne de frais'),
		 'amount' : fields.float('Montant'),
		 'line_id' : fields.many2one('student.student','Student'),
		}


	@api.onchange('fees_struct_line_id')
	def onchange_fees_struct_line_id(self):
		if self.fees_struct_line_id:
			self.amount = self.fees_struct_line_id.amount

class student_student(osv.osv):

	def _get_external_name(self,cr,uid,ids,param1,param2,context=None):
		res = {}
		for record in self.browse(cr,uid,ids):
			res[record.id] = record.name.encode('utf-8')
			if record.last:
				res[record.id] = record.name.encode('utf-8')+" "+record.last.encode('utf-8')
		return res

	def _get_parent_user_id(self,cr,uid,ids,field_name,args,context=None):
		res = {}
		for student in self.browse(cr,uid,ids):
			parent_id = student.partner_id.parent_id.id
			user_id = self.pool['res.users'].search(cr,uid,[('partner_id','=',parent_id)])
			if user_id:
				res[student.id] = user_id[0]
		return res
	
	def _search_parent_user_id(self, cr, uid, obj, field_name, args, context=None):
		student_ids = []
		for arg in args:
			(key,operator,value) = arg
			if key == "student_parent_user_id":
				user = self.pool['res.users'].browse(cr,uid,value)
				break
		if user:
			child_ids = user.partner_id.child_ids
			student_ids = self.search(cr,uid,[('partner_id','in',[child.id for child in child_ids])])
		return [('id', 'in',student_ids)]

	_inherit = 'student.student'
	_rec_name = 'last_name'
	_columns = {   
		'last_name'  : fields.function(_get_external_name,string='Nom et Prénom',type="char",store=True),
		'middle': fields.char('Middle Name', size=64, states={'done':[('readonly',True)]}),
		'last': fields.char('Surname', size=64, states={'done':[('readonly',True)]}),
		'nom_prenom_arab' : fields.char("الإسم و النسب"),
		'date_depart' : fields.date("date de départ"),
		'birth_palce_arab' : fields.char("مكان الازدياد"),
		'pricelist_ids' : fields.one2many('student.pricelist','line_id',string='Liste des prix'),
     	'student_parent_user_id' : fields.function(_get_parent_user_id,type='many2one',relation='res.users',fnct_search=_search_parent_user_id,string='Student parent user id'),
    }

	@api.multi
	def write(self, vals):
		if 'pricelist_ids' in vals:
			if self.env.context and self.env.context.get('install_mode'):
				pricelist_ids = vals.get('pricelist_ids')
				for op1,op2,line in pricelist_ids:
					for old_line in self.pricelist_ids:
						if line.get('fees_struct_line_id') == old_line.fees_struct_line_id.id:
							old_line.unlink()
		return osv.osv.write(self, vals)

class hr_employee(osv.osv):
	_name = 'hr.employee'
	_inherit = 'hr.employee'
	_columns = {   
		'nom_prenom_arab' : fields.char("الإسم و النسب"),
		'cin' : fields.char("CIN"),
		'personne_a_charge' : fields.char("Personne à charge"),
		'numero_rcp' : fields.integer("Numéro RCP"),
		'annees_experience' : fields.integer("Années d'expérience"),
		'date_embauche' : fields.date("Date d'embauche"),
		}
	#_sql_constraints = [('cin_unique', 'unique(cin)', 'cin doit être unique!')]

	

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
