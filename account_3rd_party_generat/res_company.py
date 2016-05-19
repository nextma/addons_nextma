# -*- coding: utf-8 -*-
##############################################################################
#
#    account_3rd_party_generat module for OpenERP, Module to generate account number
#                                                  for customer and supplier
#    Copyright (C) 2010-2011 SYLEAM (<http://www.syleam.fr/>)
#              Christophe CHAUVET <christophe.chauvet@syleam.fr>
#
#    This file is a part of account_3rd_party_generat
#
#    account_3rd_party_generat is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    account_3rd_party_generat is distributed in the hope that it will be useful,
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
from openerp.tools.translate import _


class AccountGeneratorType(osv.osv):
    _name = 'account.generator.type'
    _description = 'Account generator customize per type'

    _columns = {
        'partner_type': fields.selection([('customer', 'Customer'), ('supplier', 'Supplier')], 'Type', required=True, help='Select the type of partner'),
        'code': fields.char('code', size=16, required=True, help='Code use to store value in the database'),
        'name': fields.char('Name', size=64, required=True, translate=True, help='Name appear on the partner form'),
        'default_value': fields.boolean('Default value', help='Default value for this type'),
        'lock_partner_name': fields.boolean('Lock partner name', help='Partner\'s name is locked when his account has at least one account move'),
        'ir_sequence_id': fields.many2one('ir.sequence', 'Sequence', help='Sequence use to generate the code'),
        'account_template_id': fields.many2one('account.account.template', 'Account template', help='Account use to create the new one'),
        'account_parent_id': fields.many2one('account.account', 'Parent account', help='Select the parent account of the new account generate'),
        'account_reference_id': fields.many2one('account.account', 'Account reference', help='If no sequence define, this account reference is choose all the time'),
        'company_id': fields.many2one('res.company', 'Company', help='Company where this configuration is apply', required=True),
        'field_select': fields.selection([('none', ''), ('name','name'), ('ref','ref')], 'Select Field', help="Select the field where the code be generate" ),
        'code_pre': fields.char('Code Prefix', size=64, ),
        'code_suf': fields.char('Code Suffix', size=64, ),
        'code_seq_id': fields.many2one('ir.sequence', 'Sequence', domain=[('code', '=', 'res.partner')]),
    }

    _defaults = {
        'partner_type': False,
        'default_value': False,
        'ir_sequence_id': False,
        'account_template_id': False,
        'account_parent_id': False,
        'field_select': 'none',
    }

    def onchange_partner_type(self, cr, uid, ids, partner_type=None, context=None):
        """
        When partner type change, we must change domain for:
        - account_template_id
        - account_parent_id
        """
        if partner_type is None or partner_type == False:
            domain = {
                'account_template_id': [('id', '=', 0)],
                'account_parent_id': [('id', '=', 0)],
                'account_reference_id': [('id', '=', 0)],
            }
        elif partner_type == 'customer':
            domain = {
                'account_template_id': [('type', '=', 'receivable')],
                'account_parent_id': [('type', 'in', ('view', 'receivable'))],
                'account_reference_id': [('type', '=', 'receivable')],
            }
        elif partner_type == 'supplier':
            domain = {
                'account_template_id': [('type', '=', 'payable')],
                'account_parent_id': [('type', 'in', ('view', 'payable'))],
                'account_reference_id': [('type', '=', 'payable')],
            }
        else:
            raise osv.except_osv(_('Error'), _('Error in process, contact your administrator!'))
        return {'value': {}, 'domain': domain}

AccountGeneratorType()


class ResCompany(osv.osv):
    _inherit = 'res.company'

    _columns = {
        'account_generator_type_ids': fields.one2many('account.generator.type', 'company_id', 'Account generator type'),
    }

ResCompany()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
