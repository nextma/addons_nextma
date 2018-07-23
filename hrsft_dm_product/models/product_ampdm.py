# coding: utf-8
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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

#!/usr/bin/python -tt
from openerp import models, fields , api , time , tools


class ProductTemplate(models.Model):
    
    _inherit = 'product.template'

    
    
    ampdm_gmdn = fields.Char('GMDN',help="Global Medical Device Nomenclature  est la nomenclature de référence pour l'identification des dispositifs médicaux à l'échelle internationale")
    ampdm_hscode = fields.Char('HS Code',help="Le HS code (Harmonized System Codes) est un code de reconnaissance internationale utilisé principalement dans l'établissement de la nomenclature douanière nationale et la collecte des statistiques du commerce mondial")
    cedm_num = fields.Char('Numéro CEDM', help=" Numéro du certificat d'enregistrement du dispositif médical.")
    cedm_date_deb = fields.Date('Date Début', required=False , help="Date Début du certificat.")
    cedm_date_fin = fields.Date('Date Fin', required=False , help="Date Fin du certificat.")
    code_anam = fields.Char('Code ANAM' , help="Code de l'Agence Nationale de l'Assurance Maladie (ANAM) ")
    anam_tarif = fields.Char('Tarif ANAM', help="Tarif ANAM")

    classif = fields.Many2one('product.classification','Classification des DM' , help ="Classification des dispositifs medicaux")
    achat_import = fields.Boolean('Achat Import',default=False,readonly=False,required=False)
    achat_locaux = fields.Boolean('Achat Locaux',default=False,readonly=False,required=False)
    dm_ok = fields.Boolean('DM',default=False , help= "Selectionner si vous voulez ajouter les dispositifs médicaux")

class ProductDetails(models.Model):
    _name = 'product.classification'

    name = fields.Char(string="Classification" ,help="Classification du produit" , required=True)
    text = fields.Text(string="Description")


   