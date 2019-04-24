# -*- coding: utf-8 -*-

from odoo import models, fields, api
#import logging

#_logger = logging.getLogger(__name__)


class ModePaiement(models.Model):
    _name = 'hrsft_mode_paiement.mode_paiement'

    name = fields.Char(string="payment method")
    description = fields.Char(string="description for payment mode")


class ModePaiementToPartner(models.Model):
    _inherit = 'res.partner'

    mode_payment = fields.Many2one('hrsft_mode_paiement.mode_paiement', string='Méthode de payement')


class ModePaiementToSale(models.Model):
    _inherit = 'sale.order'

    mode_payment = fields.Many2one('hrsft_mode_paiement.mode_paiement', string='Méthode de payement')

    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_Sale(self):
        # _logger.info('---------------------onchange_partner_id -----------------')

        if not self.partner_id:
            self.update({
                'mode_payment': False,
            })
            return
        # _logger.info('------  mode_pay_partner -----  %s', mode_pay_partner)

        values = {'mode_payment': self.partner_id.mode_payment and self.partner_id.mode_payment.id or False}

        self.update(values)


class ModePaiementToPurchase(models.Model):
    _inherit = 'purchase.order'

    mode_payment = fields.Many2one('hrsft_mode_paiement.mode_paiement', string='Méthode de payement')


    @api.multi
    @api.onchange('partner_id')
    def onchange_partner_Purchase(self):
        # _logger.info('---------------------onchange_partner_id -----------------')

        if not self.partner_id:
            self.update({
                'mode_payment': False,
            })
            return
        # _logger.info('------  mode_pay_partner -----  %s', mode_pay_partner)

        values = {'mode_payment': self.partner_id.mode_payment and self.partner_id.mode_payment.id or False}

        self.update(values)