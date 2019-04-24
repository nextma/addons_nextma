# -*- coding: utf-8 -*-
{
    'name': "simple payment method ",

    'summary': """
       For simple payment method ;to add text like : check ; cash ; transfer to partner """,

    'description': """
        Ajoute le mode de paiement a configurer dans Comptabilte - Configuration - Mode de paiement simple , a parametrer dans la fiche client ou fournisseur et seras appliquer dans le flux vente et achat  . 
    """,

    'author': "Horiyasoft",
    'website': "http://www.horiyasoft.com",
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'payment',
    'version': '11.1.0.0',
    'images': ['static/description/banner.png'],

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale','purchase'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'data/data.xml'
    ],
    'application': True,
    'installable': True
