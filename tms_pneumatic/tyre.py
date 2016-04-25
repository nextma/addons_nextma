# -*- coding: utf-8 -*-
##############################################################################
#
#    
#
##############################################################################

from datetime import date
from twisted.test.raiser import RaiserException

from openerp import models, fields, api , _
from openerp.exceptions import except_orm


class tms_pneumatic(models.Model):

        
    _name = "tms.tyre.serial"
    _rec_name = "lot_id"
    user_id = fields.Many2one('res.users', string='Responsable',
        default=lambda self: self.env.user,readonly=True)
    lot_id = fields.Many2one('stock.production.lot',string='Numéro de série',domain="[('product_id','=',product_id)]",required=True)
    product_id = fields.Many2one('product.product',string='Article',domain="[('product_tmpl_id.tyre','=',True)]",required=True)
    brand_id = fields.Many2one('product.brand',related="product_id.brand_id",string="Marque")
    calculate_odometer_value = fields.Float('Compteur calculé',compute='_compute_odometer_value')
    odometer_value = fields.Float('Compteur réel')
    current_vehicle_id = fields.Many2one('fleet.vehicle',string='Véhicle')
    position = fields.Selection([('front_right','Avant droit'),('front_left','Avant gauche'),('back_right','Arrière droit'),('back_left','Arrière gauche')],string='Position du pneu')
    state = fields.Selection([('draft','Brouillon'),('free','Demonté'),('used','Monté')],default='draft')
    vehicle_history_ids = fields.One2many('tms.fleet.tyre','tyre_id',string='Historique de montage/demontage Pneu')

    _sql_constraints = [
         ('name_uniq', 'unique(lot_id,product_id)', "Le pneu doit être créer une seule fois!"),
    ] 
    @api.one
    @api.depends('vehicle_history_ids','current_vehicle_id')
    def _compute_odometer_value(self):
        current_odometer = 0.0
        for line in self.vehicle_history_ids:
            current_odometer += line.km_total
        self.calculate_odometer_value = current_odometer 


    @api.one
    def action_mount(self,vals):
        '''
        traiter les cas où le vehicle a déja une roue montée à la position donnée#
        '''
        fleet_tyre_obj = self.env["tms.fleet.tyre"]
        tms_tyre_obj = self.env["tms.tyre.serial"]
        vehicle_and_position = tms_tyre_obj.search([('position','=',vals.get('position')),('current_vehicle_id','=',vals.get('vehicle_id'))])
        """
        if vehicle_and_position :
            for tyre in vehicle_and_position:
                raise except_orm(_('Pneu déjà monté!'),
                _("Le pneu: %s est déjà monté à cette position.Veuillez le de-monter avant de le re-monter.")%(tyre.lot_id.name,))
        """
        self._cr.execute('update tms_fleet_tyre set status=%s where tyre_id=%s',(False,vals.get('tyre_id'),))
        previous = self.env["tms.fleet.tyre"].search([('tyre_id','=',vals.get('tyre_id')),('end_date','>',vals.get('start_date'))])
        if previous:
            raise except_orm(_('Date de début!'),
                _("La date de début n'est pas correctes"))
        fleet_tyre_obj.create(vals)
        self.current_vehicle_id = vals.get('vehicle_id')
        self.position = vals.get('position')
        self.state = 'used'

    @api.multi
    def action_demount(self,vals):
        fleet_tyres = self.env["tms.fleet.tyre"].search([('status','=',True),('vehicle_id','=',self.current_vehicle_id.id)],limit=1)
        for fleet_tyre in fleet_tyres:
            if vals.get('end_odometer') < fleet_tyre.start_odometer:
                raise except_orm(_('Erreur du compteur fin!'),
                                 _("Le compteur véhicule fin doit être >= au compteur véhicule début."))
            fleet_tyre.write({'end_date':vals.get('end_date'),'status':False,'end_odometer':vals.get('end_odometer'),'notes':vals.get('notes')})
        self.current_vehicle_id = False
        self.position = False
        self.state = 'free'

class tms_fleet_tyre(models.Model):
        
    _name = "tms.fleet.tyre"

    user_id = fields.Many2one('res.users', string='Responsable',
        default=lambda self: self.env.user,readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle',string='Véhicle')
    tyre_id = fields.Many2one('tms.tyre.serial',string='Modèle pneu')
    position = fields.Selection([('front_right','Avant droit'),('front_left','Avant gauche'),('back_right','Arrière droit'),('back_left','Arrière gauche')],string='Position du pneu')
    start_date = fields.Datetime('Date début')
    end_date = fields.Datetime('Date fin')
    status = fields.Boolean('Actif',readonly=True)
    start_odometer = fields.Float("Compteur Véhicle Début")
    end_odometer = fields.Float("Compteur Véhicle Fin")
    km_total  = fields.Float('Km Total',compute='_compute_km_total')
    notes = fields.Text('Notes')

    @api.one
    @api.depends('start_odometer','end_odometer')
    def _compute_km_total(self):
        diff = self.end_odometer - self.start_odometer
        self.km_total = 0
        if diff > 0:
            self.km_total = self.end_odometer - self.start_odometer

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        #if self.search([('vehicle_id','=',vals.get('vehicle_id')),('tyre_id','=',vals.get('tyre_id'))])
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        return models.Model.write(self, vals)

    @api.onchange('vehicle_id')
    def get_vehicle_odometer(self):
        self.vehicle_odometer =  self.vehicle_id.fuel_odometer


    
class product_template(models.Model):

        
    _inherit = "product.template"
    
    brand_id = fields.Many2one('product.brand',string='Marque')
    tyre  = fields.Boolean('est un Pneu')
    odometer = fields.Float('Compteur Pneu')
    
class product_product(models.Model):

        
    _inherit = "product.product"
    
    brand_id = fields.Many2one(comodel_name='product.brand',string='Marque',related="product_tmpl_id.brand_id")
    tyre  = fields.Boolean(string='Pneu',related='product_tmpl_id.tyre')
    odometer = fields.Float(string='Compteur Pneu',related='product_tmpl_id.odometer')

class product_brand(models.Model):
        
    _name = "product.brand"

    name = fields.Char(string='Nom de la marque')
    