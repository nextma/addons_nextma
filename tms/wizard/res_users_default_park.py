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
from openerp import _

__author__ = "NEXTMA"
__version__ = "0.1"
__date__ = "23 Décembre 2013"


class res_users_default_park(osv.osv_memory):

    _name = 'res.users.default.park'
    _description = 'Parc par defaut'
 
    def _default_park(self, cr, uid, context=None):
        object_user=self.pool.get('res.users').browse(cr,uid,uid)
        if object_user:
            return object_user.park_id and object_user.park_id.id or False        
        return False
 
    _columns = {
            'park_id' : fields.many2one('fleet.park', 'Parc', required="True"),
                    }
    _defaults = {  
        'park_id': _default_park,
        }
 
    def action_validate_default_park(self,cr,uid,ids,context={}):
        if ids:
            for object_default_park in self.browse(cr,uid,ids):
                if object_default_park.park_id:
                    cr.execute('update res_users set park_id = %d where id = %d' %(object_default_park.park_id.id,uid))
                    cr.commit()
        return {'type': 'ir.actions.act_window_close'}
    
res_users_default_park()
