# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution    
#    Copyright (C) 2004-2010 Tiny SPRL (http://tiny.be). All Rights Reserved
#    
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see http://www.gnu.org/licenses/.
#
##############################################################################

import convertion
from openerp import api
from openerp.osv import fields, osv


class account_invoice(osv.osv):
    
    _inherit = "account.invoice"
    
    _columns ={
    'numero_facture' : fields.char('Numero facture'),
    'partner_delivery_id' : fields.many2one('res.partner','Partenaire livraison'),
    'picking_ids' : fields.one2many('tms.picking','invoice_id','Bls'),
    }

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'tms.report_invoice')

    @api.multi
    @api.depends('amount_total')
    def get_amount_letter(self):
        amount = convertion.trad(self.amount_total,'DH')
        return amount

    
    def update_invoices(self, cr, uid, inv_type='out_invoice', context=None):
        move_obj = self.pool.get('tms.picking')
        invoice_ids = self.search(cr,uid,[('type','=','out_invoice')])
        print "**************************************************"
        for invoice in self.browse(cr,uid,invoice_ids):
            amount = 0.0
            for move in invoice.picking_ids:
                amount +=move.amount_total_ht 
            if invoice.amount_untaxed != amount and invoice.picking_ids:
                #for line in invoice.invoice_line:
                    #line.unlink()
                strstr = str(invoice.id) + "/" + str(invoice.number) + "/" + str(invoice.partner_id.name)
                print strstr
                #context.update({'grouped_by_product':'travel_and_type'})
                #move_obj._invoice_create_line(cr,uid,invoice.id,invoice.picking_ids,2,'out_invoice',context=context)
        print "**************************************************"


class account_invoice_line(osv.osv):
    
    _inherit = "account.invoice.line"
    
    _columns ={
    'merchandise_id' : fields.many2one('tms.travel.palet.merchandise','Type',readonly=True),
    'vehicle_id' : fields.many2one('fleet.vehicle','Vehicle',readonly=True),
    }

