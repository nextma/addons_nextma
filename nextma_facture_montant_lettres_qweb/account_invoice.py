# -*- encoding: utf-8 -*-


import convertion
from openerp import api
from openerp.osv import osv


class account_invoice(osv.osv):
    
    _inherit = "account.invoice"

    @api.multi
    def invoice_print(self):
        """ Print the invoice and mark it as sent, so that we can see more
            easily the next step of the workflow
        """
        assert len(self) == 1, 'This option should only be used for a single id at a time.'
        self.sent = True
        return self.env['report'].get_action(self, 'nextma_facture_montant_lettres_qweb.report_invoice')

    @api.multi
    @api.depends('amount_total')
    def get_amount_letter(self):
        amount = convertion.trad(self.amount_total,'DH')
        return amount

