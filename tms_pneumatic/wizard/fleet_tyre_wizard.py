# -*- coding: utf-8 -*-
##############################################################################
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
from datetime import date,datetime


from openerp import models, fields, api


class fleet_tyre_mount_wizard(models.TransientModel):
    _name = "fleet.tyre.wizard"
    
    user_id = fields.Many2one('res.users', string='Responsable',
        default=lambda self: self.env.user,readonly=True)
    vehicle_id = fields.Many2one('fleet.vehicle',string='Véhicle',required=True)
    tyre_id = fields.Many2one('tms.tyre.serial',string='Modèle pneu',default=lambda self: self.env.context['active_id'],required=True)
    position = fields.Selection([('none','Non pertinent'),('front_right','Avant droit'),('front_left','Avant gauche'),('back_right','Arrière droit'),('back_left','Arrière gauche')],string='Position du pneu',default="none")
    start_date = fields.Datetime('Date début',required=True,default=datetime.today(), helps="Date réelle d'affectation du pneu au vehicle")
    vehicle_odometer = fields.Integer('Compteur du véhicle')
    notes = fields.Text('Notes')
    @api.multi
    def action_mount(self):
        vals = {
            'vehicle_id':self.vehicle_id.id,
            'tyre_id':self.tyre_id.id,
            'position':self.position,
            'start_date':self.start_date,
            'vehicle_odometer':self.vehicle_odometer,
            'status':True,
            }
        self.tyre_id.action_mount(vals)

class fleet_tyre_demount_wizard(models.TransientModel):
    _name = "fleet.tyre.demount.wizard"

    
    def _default_end_odometer(self):
        default_end_odometer = 0.0
        tyre = self.env['tms.tyre.serial'].browse(self.env.context['active_id'])
        fleet_tyres = self.env["tms.fleet.tyre"].search([('status','=',True),('vehicle_id','=',tyre.current_vehicle_id.id)],limit=1)
        if fleet_tyres:
            default_end_odometer = fleet_tyres[0].start_odometer
        return default_end_odometer

    tyre_id = fields.Many2one('tms.tyre.serial',string='Modèle pneu',default=lambda self: self.env.context['active_id'],required=True)
    end_date = fields.Datetime('Date fin',required=True,default=datetime.today(), helps="Date réelle de demontage du pneu du vehicle")
    end_odometer = fields.Float("Compteur Véhicle Fin",required=True,default=_default_end_odometer)
    notes = fields.Text('Notes')
   
    
    @api.multi
    def action_demount(self):
        vals = {
            'end_date':self.end_date,
            'end_odometer': self.end_odometer,
            'notes' : self.notes,
            }
        self.tyre_id.action_demount(vals)
