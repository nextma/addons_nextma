{
    'name': "simple payment method ",

    'summary': """
       For simple payment method ;to add text like : check ; cash ; transfer to partner """,

    'description': """
        Simple payment method description to your invoices ; add sub menu simple_payment_mode 
        to  " account configuration manager" then partner can use this for his model . 
    """,

    'author': "Horiyasoft",
    'website': "http://www.horiyasoft.com",
    'images': [],

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/10.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'payment',
    'version': '1.0.0',

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
}
