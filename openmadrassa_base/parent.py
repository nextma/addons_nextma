# -*- coding: utf-8 -*-
#/#############################################################################
#
#    Tech-Receptives Solutions Pvt. Ltd.
#    Copyright (C) 2004-TODAY Tech-Receptives(<http://www.tech-receptives.com>).
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
#/#############################################################################
from openerp.osv import osv, fields

class student_parent(osv.osv):
    _name = 'student.parent'

    _columns = {

            'name': fields.many2one('res.partner','Parent Name', required=True,domain="[('is_company','=',True)]"),
            'student_ids': fields.many2many('student.student', 'student_parent_student_student_rel', 'student_parent_id', 'student_id', string="Enfants"),
            #'user_id': fields.many2one('res.users', 'User', required=True),
    }
    def create(self,cr,uid,vals,context=None):
        id = super(student_parent,self).create(cr,uid,vals,context=context)
        if len(vals.get('student_ids')[0][2]) == 0:
            partner_ids = self.pool['res.partner'].search(cr,uid,[('parent_id','=',vals.get('name'))])
            self.pool['res.partner'].write(cr,uid,partner_ids,{'parent_id':False,'use_parent_address':False})
            return id
        cr.execute('select partner_id from res_users ru,student_student ss where ru.id=ss.user_id and ss.id in %s',(tuple(vals.get('student_ids')[0][2]),))
        partners  = cr.fetchall()
        partner_ids = [partner[0] for partner in partners]
        self.pool['res.partner'].write(cr,uid,partner_ids,{'parent_id':vals.get('name'),'use_parent_address':True})
        return id
    def write(self,cr,uid,ids,vals,context=None):
        student_parent_link = self.browse(cr,uid,ids)
        parent_id = vals.get('name') or student_parent_link[0].name.id
        student_ids = vals.get('student_ids') and vals.get('student_ids')[0][2] or [student.id for student in student_parent_link[0].student_ids]
        print student_ids
        
        
        partner_ids_old = self.pool['res.partner'].search(cr,uid,[('parent_id','=',parent_id)])
        self.pool['res.partner'].write(cr,uid,partner_ids_old,{'parent_id':False,'use_parent_address':False})
        
        
        cr.execute('select partner_id from res_users ru,student_student ss where ru.id=ss.user_id and ss.id in %s',(tuple(student_ids),))
        partners  = cr.fetchall()
        partner_ids_new = [partner[0] for partner in partners]
        self.pool['res.partner'].write(cr,uid,partner_ids_new,{'parent_id':parent_id,'use_parent_address':True})
        return super(student_parent,self).write(cr,uid,ids,vals,context=context)

    def _check_parent_uniq_future(self,cr,uid,ids,vals):
        if len(ids) >= 1:
            student_parent_link = self.browse(cr,uid,ids)
            student_ids = vals.get('student_ids') and vals.get('student_ids')[0][2] or [student.id for student in student_parent_link[0].student_ids]
        else:
            student_ids = student_ids = vals.get('student_ids') and vals.get('student_ids')[0][2] or []
        parent_id = vals.get('name') or student_parent_link[0].name.id
        print parent_id
        cr.execute('select student_id from student_parent_student_student_rel where  student_id  in %s',(tuple(student_ids),))
        res = cr.fetchall()
        if res:
            raise Warning(_('Un étudiant doit avoir un seul parent.')) 
student_parent()
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
