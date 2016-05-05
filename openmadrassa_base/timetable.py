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
from openerp import _
from openerp.exceptions import Warning

class time_table_line(osv.Model):
    
    _inherit = 'time.table.line'
    _order = "sequence,start_time"

    def _get_sequence(self,cr,uid,ids,fields_name,args,context=None):
        res = {}
        data = {'monday':1,'tuesday':2,'wednesday':3,'thursday':4,'friday':5,'saturday':6,'sunday':7}
        for rec in self.browse(cr,uid,ids):
            if rec.week_day in data:
                res[rec.id] = data[rec.week_day]
            else:
                res[rec.id] = 0
        return res
                
                
                
    _columns = {
                'standard_id': fields.related('table_id','standard_id',type='many2one',relation='school.standard', string='Academic Class', required=True,readonly=True),
                'year_id': fields.related('table_id','year_id',type='many2one',relation='academic.year',string= 'Year', required=True,readonly=True),                  
                'timetable_type': fields.related('table_id','timetable_type',type='char',string= "Type d'emploi du temps", required=True,readonly=True),                  
                'sequence' : fields.function(_get_sequence,type='integer',string='Sequence',store=True),
                'color' : fields.integer('Color Index'),
                }

    def write(self,cr,uid,ids,vals,context=None):
        user_groups = self.pool['res.users'].browse(cr,uid,uid).groups_id
        user_groups_ids  = [group.id for group in user_groups]
        admin_school_group_id = self.pool['ir.model.data'].xmlid_to_res_id(cr,uid,'school.group_school_administration')
        if admin_school_group_id not in user_groups_ids:
            if 'week_day' in vals:
                raise Warning(_('Vous ne pouvez pas effectuer ce déplacement.')) 
        return super(time_table_line,self).write(cr,uid,ids,vals,context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: