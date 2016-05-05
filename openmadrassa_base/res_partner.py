# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

from openerp.osv import osv, fields


class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns= {
        'discount' :  fields.float('Remise accordée(%)'),
        'is_company': fields.boolean('Est un parent', help="Cochez cette case, s'il s'agit d'un parent d'élève"),
        }

class res_users(osv.osv):
    _inherit = 'res.users'
    
    def write(self,cr,uid,ids,vals,context=None):
        partner_pool = self.pool["res.partner"]
        res = super(res_users,self).write(cr,uid,ids,vals,context=context)
        user = self.browse(cr,uid,ids[0])
        if self.has_group(cr, ids[0], "school.group_school_parent"):
            partner_pool.write(cr,uid,user.partner_id.id,{'is_company':True,'customer':True})
        else:
            partner_pool.write(cr,uid,user.partner_id.id,{'is_company':False})
        return res

    def create(self,cr,uid,vals,context=None):
        partner_pool = self.pool["res.partner"]
        res = super(res_users,self).create(cr,uid,vals,context=context)
        user = self.browse(cr,uid,res)
        if self.has_group(cr, res, "school.group_school_parent"):
            partner_pool.write(cr,uid,user.partner_id.id,{'is_company':True,'customer':True})
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
