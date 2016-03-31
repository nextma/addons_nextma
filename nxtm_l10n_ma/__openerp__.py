# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010 kazacube (http://kazacube.com).
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
    'name' : 'Comptabilité - Maroc PCG',
    'version' : '1.0',
    'author' : 'kazacube,nextma',
    'category' : 'Localization/Account Charts',
    'description': """
Ceci est le module de base pour gérer le plan comptable marocain.
=================================================================

Ce Module charge le modèle du plan de comptes standard Marocain et permet de
générer les états comptables aux normes marocaines (Bilan, CPC (comptes de
produits et charges), balance générale à 6 colonnes, Grand livre cumulatif...).
L'intégration comptable a été validé avec l'aide du Cabinet d'expertise comptable
Seddik au cours du troisième trimestre 2010.""",
    'website': 'http://www.kazacube.com',
    'depends' : ['base', 'account','account_accountant'],
    'data' : [
        'security/ir.model.access.csv',
        #'l10n_ma_pre_install.yml',
        'account_type.xml',
        'account_pcg_maroc.xml',
        'nxtm_l10n_ma_wizard.xml',
        'nxtm_l10n_ma_tax.xml',
        'nxtm_l10n_ma_journal.xml',
        'res_currency_data.xml',
        'partner_view.xml',
        'nxtm_l10n_ma_view.xml',
    ],
    'demo' : [],
    'auto_install': False,
    'installable': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

