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

from openerp.osv import fields, osv
from openerp.tools.translate import _

__author__ = "NEXTMA"
__version__ = "0.1"
__date__ = u"21 Janvier 2014"

class fleet_service_type(osv.Model):
    _name = 'fleet.service.type'
    _inherit = 'fleet.service.type'

    MAINTENANCE_TYPE_SELECTION1 = [
        ('bm', u'Panne'),
        ('cm', u'Corrective'),
        ('pm', u'Programmée'),
    ]

    _columns = {
        'mro_ok': fields.boolean(u'mro'),
        'maintenance_type': fields.selection(MAINTENANCE_TYPE_SELECTION1, u'Type de maintenance', required=False),
        }

fleet_service_type()
