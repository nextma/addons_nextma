# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2009 SISTHEO
#                  2010-2011 Christophe Chauvet <christophe.chauvet@syleam.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv
from openerp.osv import fields
import types


class wizard_install_third_part_accounts(osv.osv_memory):
    """
    """
    _name = 'wizard.install.third.part.accounts'

    _columns = {
        'company_id': fields.many2one('res.company', 'Company', required=True),
        'receivable_id': fields.many2one('account.account', 'Account receivable', domain="[('type', '=', 'view')]", required=True),
        'payable_id': fields.many2one('account.account', 'Account payable', domain="[('type', '=', 'view')]", required=True),
    }

    def _default_account_id(self, cr, uid, account_type, context=None):
        if context is None:
            context = {}
        account_type_id = self.pool.get('account.account.type').search(cr, uid, [('code', '=', account_type)], context=context)
        srch_args = [('type', '=', 'view'), ('user_type', 'in', account_type_id)]
        account_id = self.pool.get('account.account').search(cr, uid, srch_args, context=context)
        if account_id:
            if type(account_id) is types.IntType:
                return account_id
            elif type(account_id) is types.ListType:
                return account_id[0]
        return False

    def _default_receivable_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        return self._default_account_id(cr, uid, 'receivable', context=context)

    def _default_payable_id(self, cr, uid, context=None):
        if context is None:
            context = {}
        return self._default_account_id(cr, uid, 'payable', context=context)

    _defaults = {
        'company_id': lambda self, cr, uid, c: self.pool.get('res.users').browse(cr, uid, [uid], c)[0].company_id.id,
        'receivable_id': _default_receivable_id,
        'payable_id': _default_payable_id,
    }

    def _set_property(self, cr, uid, prop_name, prop_account_id, company_id):
        """
        Set/Reset default properties
        """
        property_obj = self.pool.get('ir.property')
        prp_ids = property_obj.search(cr, uid, [('name', '=', prop_name), ('company_id', '=', company_id)])
        # FIXME Add critéria to find only 1 record
        if prp_ids:
            if len(prp_ids) == 1:  # the property exist: modify it
                vals = {
                    'value': prop_account_id and 'account.account,' + str(prop_account_id) or False,
                }
                out_id = prp_ids[0]
                property_obj.write(cr, uid, [out_id], vals)
            else:
                #FIXME Over write the nly record that have res = NULL
                out_id = False
                pass    # DO NOTHING / DO NOT CHANGE EXISTING DATAS
        else:  # create the property
            fields_obj = self.pool.get('ir.model.fields')
            field_ids = fields_obj.search(cr, uid, [('name', '=', prop_name), ('model', '=', 'res.partner'), ('relation', '=', 'account.account')])
            vals = {
                'name': prop_name,
                'company_id': company_id,
                'fields_id': field_ids[0],
                'value': prop_account_id and 'account.account,' + str(prop_account_id) or False,
            }
            out_id = property_obj.create(cr, uid, vals)
        return out_id

    def action_start_install(self, cr, uid, ids, context=None):
        """
        Create the properties : specify default account (payable and receivable) for partners
        """
        wiz_data = self.browse(cr, uid, ids[0])
        self._set_property(cr, uid, 'property_account_receivable', wiz_data.receivable_id and wiz_data.receivable_id.id, wiz_data.company_id and wiz_data.company_id.id)
        self._set_property(cr, uid, 'property_account_payable', wiz_data.payable_id and wiz_data.payable_id.id, wiz_data.company_id and wiz_data.company_id.id)

        next_action = {
            'type': 'ir.actions.act_window',
            'res_model': 'ir.actions.configuration.wizard',
            'view_type': 'form',
            'view_mode': 'form',
            'target': 'new',
        }
        return next_action

    def action_cancel(self, cr, uid, ids, conect=None):
        return {'type': 'ir.actions.act_window_close'}

wizard_install_third_part_accounts()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
