# -*- coding: utf-8 -*-


{
    'name': 'Check Printing Base FR',
    'version': '1.0',
    'category': 'Accounting',
    'author': 'HORIYASOFT,Odoo S.A',
    'summary': 'Check printing adaptation french',
    'license': 'AGPL-3',
    'description': """
This module offers the basic functionalities to make payments by printing checks in Frensh
It must be used as a dependency for modules that provide country-specific check templates.
The check settings are located in the accounting journals configuration page.
    """,
    'website': 'www.horiyasoft.com',
    'depends': ['account'],
    'data': [
        'data/account_check_printing_data.xml',
        'views/account_journal_views.xml',
        'views/account_payment_views.xml',
        'wizard/print_prenumbered_checks_views.xml'
    ],
    'images': ['static/description/banner.jpeg'],
    'installable': True,
    'auto_install': False,
}




