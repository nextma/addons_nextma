# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

#import logging

from openerp.osv import fields, osv
from openerp import pooler
from openerp.tools.translate import _

#_logger = logging.getLogger(__name__)


class tms_gmao_config_wizard(osv.osv_memory):
    _name = 'tms.gmao.config.settings'
    _inherit = 'res.config.settings'
    _columns = {
        #'default_foo': fields.type(..., default_model='my.model'),
        'tms_gmao_param_current_counter': fields.boolean(u'Compteur sur base des voyages (Oui), Compteur sur base des bons de carburant (Non)', group='base.group_user', implied_group=''),
        'tms_gmao_param_mro_order_supply_chain': fields.boolean(u'Supply chain dans les ordres de maintenance', group='base.group_user', implied_group=''),
        #'': fields.boolean(u'', group='base.group_user', implied_group=''),
        #'module_baz': fields.boolean(...),
        #'other_field': fields.type(...),
        }

    _defaults = {
        'tms_gmao_param_current_counter': lambda *a:True,
        'tms_gmao_param_mro_order_supply_chain': lambda *a:False,
        }

tms_gmao_config_wizard()
