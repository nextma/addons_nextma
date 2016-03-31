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

from openerp.osv import fields, osv
from openerp.tools.translate import _

class picking_terminer(osv.osv_memory):
    _name = "picking.terminer"
    _description = "Pickings Terminer"
  
    def view_init(self, cr, uid, fields_list, context=None):
        if context is None:
            context = {}
        record_id = context and context.get('active_id', False)
        picking = self.pool.get('tms.picking').browse(cr, uid, record_id, context=context)
        return False

    def terminer_bls(self, cr, uid, ids, context=None):
        picking_obj = self.pool.get('tms.picking')
        mod_obj = self.pool.get('ir.model.data')
        act_obj = self.pool.get('ir.actions.act_window')
        newinv = []
        if context is None:
            context = {}
        data = self.read(cr, uid, ids)[0]
        record_id = context and context.get('active_id', False)
        records=context.get('active_ids', False)
        for record in records:
            picking = self.pool.get('tms.picking').browse(cr, uid, record, context=context)
            self.pool.get('tms.picking').action_done_wkf(cr, uid,record, context=context)
        return True

picking_terminer()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
