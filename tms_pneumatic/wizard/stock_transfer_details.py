# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-TODAY OpenERP S.A. <http://www.odoo.com>
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


from openerp import models,api
from openerp.exceptions import except_orm
from openerp.tools.translate import _


class stock_transfer_details(models.TransientModel):
    _inherit = 'stock.transfer_details'
    _description = 'Picking wizard'


    @api.one
    def do_detailed_transfer(self):
        for item in self.item_ids:
            if item.lot_id.id == False and item.product_id.tyre:
                raise except_orm(_('Données manquantes!'),
                _("Merci de préciser un numéro de série pour chaque pneu"))

        if self.picking_id.picking_type_id.code == "incoming":
            for line in self.item_ids:
                if line.product_id.tyre:
                    tyre = {
                           'product_id':line.product_id.id,
                           'brand_id' : line.product_id.brand_id.id,
                           'lot_id' : line.lot_id.id,
                           }
                    ids=self.env["tms.tyre.serial"].search([('lot_id','=',tyre["lot_id"]),('product_id','=',tyre["product_id"])])
                    if len(ids)==0:
                        self.env["tms.tyre.serial"].create(tyre)

        return super(stock_transfer_details,self).do_detailed_transfer()

