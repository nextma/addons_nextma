# -*- coding: utf-8 -*-
##############################################################################
#
#    
#
##############################################################################
{
    'name' : 'TMS Pneumatic management',
    'version': '1.0',
    'author' : 'NEXTMA S.A.R.L',
    'sequence': '1',
    'category': 'Vertical functionality',
    'summary': 'Gestion de la pneumatique , montage/demontage des pneus',
    'depends' : [
                    'base', 
                    'mro',
                    'tms',
                    'tms_gmao',
                ],
    'description': '',
    'init_xml' : [],
    'data' : [
              'security/ir.model.access.csv',
              'wizard/fleet_tyre_wizard_view.xml',
              'tms_pneumatic_view.xml',
              'mro_view.xml',
              'fleet_view.xml',
              #'tms_pneumatic_data_view.xml',
               ],
     
  
    'application': True,
    'installable': True
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

