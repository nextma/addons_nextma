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
{
    'name': 'GESTION CABINET NOTAIRE MAROC ',
    'version': '1.0',
    'summary': 'GESTION CABINET NOTAIRE MAROC  - Module de Base',
    'description': """
GESTION CABINET NOTAIRE 
=====================================================
suggestions, propositions,remarquess welcome at info@nextma.com

""",
    'author': 'NEXTMA, HORIYASOFT',
    'website': 'http://www.horiyasoft.com',
    'category': 'Localization',
    'depends': [
        'account',
        'document',
        'auditlog',
        'base',

    ],
    'data': [
        'nextma_notariat_ma_sequence.xml',
        'nextma_notariat_ma_workflow.xml',
        'nextma_notariat_ma_data_travail.xml',
        'nextma_notariat_ma_data_ville.xml',
        'nextma_notariat_ma_view.xml',
        'nextma_notariat_ma_menu.xml',
        'security/notariat_ma_security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [

    ],

    'installable': True,
    'application': True,
    'auto_install': False,

    'css': [ 'static/src/css/notariat.css' ],

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
