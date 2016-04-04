# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016 NEXTMA (<http://www.nextma.com>).
#    
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
    'name': 'Sequence rfq purchase order',
    'version': "1.0",
    "description": """
Create different sequences for RFQs and Purchase Order
    """,
    'author': 'NEXTMA',
    'maintainer': 'NEXTMA',
    'website': 'http://www.nextma.com',
    'category': 'Purchase Management',
    'depends': [
    		"purchase",
	    ],
	"data":[
            "purchase_view.xml",
            "purchase_sequence.xml",
	    ],
    "demo_xml": [
	    ],
    "update_xml": [
	    ],
    "installable": True,
}
