# -*- encoding: utf-8 -*-
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
    'name': 'Facture avec le montant en lettres en Francais qweb',
    'version': '2.0.1',
    "author" : "NEXTMA,HORIYASOFT",
    'summary': """Impression montant en lettre dans le Facture""",
    "website" : "http://www.horiyasoft.com",
    'description': 'Module qui permet de  convertir le montant d/une facture en lettres (en Francais) et l"ajoute  au rapport de la facture',
    'category': 'Generic Modules/Accounting',
    'depends' : [
                    'account',
                ],
    'data' : [
              'views/report_invoice.xml',
               ],
     
    'images': ['static/description/banner.png'], 
    'application': True,
    'installable': True

}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
