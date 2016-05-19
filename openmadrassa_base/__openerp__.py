# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-2012 Serpent Consulting Services (<http://www.serpentcs.com>)
#    Copyright (C) 2013-2014 Serpent Consulting Services (<http://www.serpentcs.com>)
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
    "name" : "OpenMadrassa Base",
    "version" : "2.2.0",
    "author" : "NEXTMA, HORIYASOFT",
    "website" : "http://www.nextma.com",
    "category": "School Management",
    "complexity": "easy",
    "description": "Gestion d'école selon le contexte marocain , suggestions,remarques welcom at info@nextma.com",
    "depends" : ["account","school","school_fees",'product','timetable','exam','school_event','school_transport','school_attendance','student_evaluation'],
    "data" : [
            'security/ir.model.access.csv',
            'security/security_view.xml',
            'school_view.xml',
            'res_partner_view.xml',
            'parent_view.xml',
            'timetable_view.xml',
            'wizard/student_monthly_fees_wizard_view.xml',
            'wizard/student_payslip_invoice_view.xml',
            'student_payslip_workflow.xml',
        ],
    'demo': [
             ],
    "test" : [],

    "installable": True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
