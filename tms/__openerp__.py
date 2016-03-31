# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2010-2012 OpenERP s.a. (<http://openerp.com>).
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
    'name': 'TMS - Transport Management System',
    'version': '3.0',
    'category': 'Vertical functionality',
    'description': """
Transport Management System (TMS) for Odoo.
===================================================
    - Fleet Management \n
    - Travel Management \n
    - Travel Planning \n
    - Fuel management (internal / external) \n
    - Sales turnover of the park in real time \n
    - Managing drivers \n
    - Management of the commissions. \n
    
Transport Management System (TMS) for Odoo.
===================================================
    - Gestion de parc \n
    - Gestion de voyage \n
    - Planification de voyage \n
    - Gestion de carburant (interne/externe) \n
    - Chiffre d'affaire du parc en temps réel \n
    - Gestion des chauffeurs \n
    - Gestion des commissions \n
""",
    'author': 'NEXTMA',
    'maintainer': 'NEXTMA',
    'website': 'http://www.nextma.com',
    'icon': '/tms/static/src/img/icon.png',
    'depends': ["base","sale","hr","stock","product","purchase","analytic","fleet","account"],
    'data': [
        'data/tms_data.xml',
        'data/fleet_data.xml',
        'security/tms_security.xml',
        'security/ir.model.access.csv',
        'wizard/res_users_default_park_view.xml',
        'wizard/log_fuel_external_card_view.xml',
        'wizard/sale_make_invoice.xml',
        #'wizard/picking_make_invoice.xml',
        'wizard/picking_make_invoice2.xml',
        'wizard/picking_assigne.xml',
        'wizard/picking_terminer.xml',
        'res_config_view.xml',
        'tms_sequence.xml',
        'res_partner_view.xml',
        'hr_view.xml',
        'product_view.xml',
        'stock_view.xml',
        'sale_view.xml',
        'tms_workflow.xml',
        'tms_view.xml',
        'tms_grouping_view.xml',
        'pricelist_view.xml',
        'fleet_view.xml',
        'account_invoice_view.xml',
        #'tms_truck_view.xml',
        'tms_menu.xml',
        'tms_account_bank_statement_view.xml',
        'report_view.xml',
        'views/report_invoice.xml',
        'report/tms_picking_report_view.xml',
        'views/picking_report.xml',
        'wizard/tms_picking_report_view.xml',
        'views/picking_report_wiz.xml',
        'views/picking_report_driver_wiz.xml',
        #'views/report_heritage_invoice.xml',

    ],
    'demo': [
    ],
    'test': [
    ],
    'application': True,
    'installable': True,
    'auto_install': False,
    'css': [
        #'static/src/css/modules.css'
    ],
    'js': [
        #'static/src/js/apps.js',
    ],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
