# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
import odoo.addons.decimal_precision as dp


class StockPicking(models.Model):
    _inherit = 'account.invoice'
    
    timbre = fields.Float(string='Timbre', compute='get_payment',store=True)
    montant_avec_timbre = fields.Float(string='Montant avec Timbre', compute='get_payment')
    test = fields.Selection([
        ('avec_timbre', 'Avec Timbre'),
        ('sans_timbre', 'Sans Timbre')],
        compute ='get_filter',
        store=True,
        string='Avec/sans Timbre')
    
    #test2 = fields.Boolean('test2',default=False, compute=)
    
    
    @api.multi
    def get_filter(self):
        for record in self:
            if (record.timbre != 0.0):
                record.test ='avec_timbre'
                print 'A'
            else:
                record.test ='sans_timbre'
                print 'B'
        
    

    @api.depends('state','amount_total')
    @api.multi
    def get_payment(self):
   
        
        for r in self:
            if r.state == 'paid':
                payments = self.env['account.payment'].sudo().search([('communication', '=', r.number)])
                if payments:
                    for record in payments:
                        if record.journal_id.type == 'cash':
                            r.timbre = (float((r.amount_total)) * 25)/ 10000
                            r.montant_avec_timbre = float(r.timbre) + float(r.amount_total)
                            #r.test2 = True
                        else:
                            r.timbre = 0.0
                            r.montant_avec_timbre = float(r.amount_total)
                           
            else:
                r.timbre = 0.0
                r.montant_avec_timbre = float(r.amount_total)
                #r.test2 = False
               
        
    
   
           
    
    

    