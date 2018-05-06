# -*- coding: utf-8 -*-

{
    'name' : 'Pack',
    'author': 'Gabriel Lopez Alarcon , HORIYASOFT',
    'version' : '1',
    'summary': 'Forfaits et produits',
    'license': 'AGPL-3',
    'description': """
       
        Module spécifique pour la gestion des pack de produits  
    """,
    'category': 'Produits',
    'website': 'www.horiyasoft.com',
    'images' : [],
    'depends' : ['sale','account',],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'pack.xml'
        
        
        
    ],
    'demo': [

    ],
    'qweb': [

    ],
    'images': ['static/description/banner.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}
