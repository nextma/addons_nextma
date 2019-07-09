##############################################################################
#
#    ODOO, Open Source Management Solution
#    Copyright (C) 2017 HORIYASOFT (<www.horiyasoft.com>).
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
    'name': 'Client (RC,IF,PATENTE,ICE)',
    'version': '12.0',
    'author': 'HORIYASOFT',
    'category': 'Management',
    'summary': """Fiche partenaire Maroc""",
    'license': 'AGPL-3',
    'website': 'www.horiyasoft.com',
    'description': """Ajouts des champs RC(Registre de Commerce, IF (Identifiant Fiscale), ICE (Identifiant ommun de l'Entreprise)
dans la fiche client en conformité aux normes Maroc

    """,
    'depends': ["base"],
    'data': [
             'views/partner_view.xml',
             ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application' : True,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
