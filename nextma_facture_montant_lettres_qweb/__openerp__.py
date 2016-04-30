# -*- encoding: utf-8 -*-

{
    'name': 'Facture avec le montant en lettres en Francais(qweb)',
    'version': '1.0',
    'depends': ['account'],
    "author" : "NEXTMA",
    "website" : "http://www.nextma.com",
    'description': "Ce module permet de  convertir le montant d'une facture en lettres (en Francais) dans le rapport pdf",
    'category': 'Generic Modules/Accounting',
    'depends' : [
                    'account',
                ],
    'data' : [
              'views/report_invoice.xml',
              'report.xml',
               ],
     
  
    'application': True,
    'installable': True

}


