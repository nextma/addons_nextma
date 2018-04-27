# coding: utf-8
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
{
    'name': 'Dispositifs Medicaux',
    'version': '10.0.1.0.0',
    'author': "HORIYASOFT",
    'category': 'Industries',
    'depends': ['product'],
    'demo': [],
    'description': """
       
        Module spécifique pour la gestion des Dispositifs Medicaux  
        en ajoutant les champs dans la fiche article 
    """,

    'data': [
        'views/product_ampdm_view.xml',
        'views/classification_menu_view.xml',
        'data/default_data.xml'

    ],
    'auto_install': False,
    'installable': True,
}
