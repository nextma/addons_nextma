# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 NEXTMA (<http://www.nextma.com>).
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
    'name' : 'Balance sheet with 6 columns ',
    'version' : '1.1',
    'author' : 'NEXTMA,HORIYASOFT',
    'category': 'Accounting & Finance',
    'description' : """
Balance sheet with 6 columns ,Rapport sur la balance générale .
====================================

Ce module modifie:
--------------------------------------------
    * La balance générale par défaut en balance générale 6 colonnes ce qui permet de comparer deux années fiscales
    

    """,
    'website': 'nextma.com',
    'images' : [],
    'depends' : ['account'],
    'data': [
        'report/report_paperformat.xml',
        'account_report.xml',
        'wizard/account_report_common_view.xml',
        'views/report_trialbalance.xml',
        'static/src/css/css_style.xml',

    ],
    'qweb' : [],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
