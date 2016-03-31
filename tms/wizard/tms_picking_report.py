# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
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

from openerp import tools, api
from openerp.osv import fields, osv


class tms_picking_report_line(osv.osv_memory):
    _name = 'tms.picking.report2.line'
    _columns = {
            'driver_id' : fields.many2one('hr.employee','Chauffeur'),
            'vehicle_id' : fields.many2one('fleet.vehicle', 'Véhicle'),
            'product_id' : fields.many2one('product.product', 'Trafet'),
            'partner_id' : fields.many2one('res.partner', 'Client'),
            'date' : fields.date('Date'),
            'origin': fields.char('Num. TC'),
            'state': fields.selection([
            ('draft', u'Programmé'),
            ('cancel', u'Annulé'),
            ('confirmed', u'Plannifié'),
            ('assigned', u'Affecté'),
            ('decharge',u'Déchargé'),
            ('done', u'Terminé'),
            ], 'Etat', readonly=True, select=True, track_visibility='onchange', help=u"""
            * Brouillon: Bon de livraison voyage non encore confirmé et ne sera pas plannifié tant qu'il ne sera pas confirmé.\n
            * En attente de disponibilité: En attente de disponibilité du véhicule ou du chauffeur pour effectuer le voyage.\n
            * Assigné: Véhicule et chauffeur assignés, juste en attente de la validation de l'utilisateur.\n
            * Terminé: Voyage créé, bon de livraison validé et prêt à être facturé.\n
            * Annulé: La livraison a été annulée."""
        ),
            'report_id' : fields.many2one('tms.picking.report2','Report'),
    }
class tms_picking_report(osv.osv_memory):
    _name = 'tms.picking.report2'
    
    _columns = {
        'title' : fields.text('Titre du rapport'),
        'criteria_1': fields.selection([('used', 'Véhicules programmés'), ('unused', 'Véhicles non programmés'), ('both', 'Tous')], "Véhicules", required=True),
        'criteria_2': fields.date("Du :",required=True),
        'criteria_3' : fields.date('Au :'),
        'count' : fields.float('Nombre Total'),
        'state': fields.selection([
            ('draft', u'Programmé'),
            ('cancel', u'Annulé'),
            ('confirmed', u'Plannifié'),
            ('assigned', u'Assigné'),
            ('decharge',u'Déchargé'),
            ('done', u'Terminé'),
            ], 'Etat',select=True, track_visibility='onchange', help=u"""
            * Brouillon: Bon de livraison voyage non encore confirmé et ne sera pas plannifié tant qu'il ne sera pas confirmé.\n
            * En attente de disponibilité: En attente de disponibilité du véhicule ou du chauffeur pour effectuer le voyage.\n
            * Assigné: Véhicule et chauffeur assignés, juste en attente de la validation de l'utilisateur.\n
            * Terminé: Voyage créé, bon de livraison validé et prêt à être facturé.\n
            * Annulé: La livraison a été annulée."""
        ),
        'data_line_ids' : fields.one2many('tms.picking.report2.line','report_id','Lignes'),
    }
    _defaults = {
        "title" : "Rapport d'occupation des véhicules",
        }
    @api.multi
    def onchange_criteria_1(self,criteria_1) :
        if criteria_1 == 'both':
            return {'value':{'criteria_2':False}}

    def print_report(self, cr, uid, ids, data, context=None):
        cr.execute('DELETE from tms_picking_report2_line;')
        cr.execute("ALTER SEQUENCE tms_picking_report2_line_id_seq RESTART WITH 1;")
        for record in self.browse(cr,uid,ids):
            if record.state :
                sql = """ 
                  INSERT INTO tms_picking_report2_line(driver_id,vehicle_id,product_id,partner_id,date,state,origin) 
                    select fv.hr_driver_id,
                    fv.id,
                    tp.product_id,
                    tp.partner_id,
                    tp.date,tp.state,tp.origin FROM
                    fleet_vehicle fv
                      left join tms_picking tp on (fv.id=tp.vehicle_id)
                    where fv.active is true and tp.state=%s and fv.imprimer_rapport is true
                    order by fv.id,fv.hr_driver_id,tp.date
                      ;
                """
                cr.execute(sql,(record.state,))
            else :
                sql = """ 
                  INSERT INTO tms_picking_report2_line(driver_id,vehicle_id,product_id,partner_id,date,state,origin) 
                    select fv.hr_driver_id,
                    fv.id,
                    tp.product_id,
                    tp.partner_id,
                    tp.date,tp.state,tp.origin FROM
                    fleet_vehicle fv
                      left join tms_picking tp on (fv.id=tp.vehicle_id)
                    where fv.active is true and fv.imprimer_rapport is true
                    order by fv.id,fv.hr_driver_id,tp.date
                      ;
                """
                cr.execute(sql)
            if record.criteria_1 == 'unused' :
                sql2 = """
                        DELETE FROM tms_picking_report2_line
                        where vehicle_id in 
                        (select vehicle_id from tms_picking where date=%s)
                   """
                sql3 = """
                       DELETE FROM tms_picking_report2_line WHERE id NOT IN (
                       SELECT max(id) FROM tms_picking_report2_line
                       GROUP BY vehicle_id
                       )
                       """
                cr.execute(sql2,(record.criteria_2,))
                cr.execute(sql3)
            cr.execute('update tms_picking_report2_line set create_uid=%s,write_uid=%s',(uid,uid,))
            if record.criteria_1 == 'used' :
                if record.criteria_2:
                    if record.criteria_3:
                        cr.execute("UPDATE tms_picking_report2_line set report_id=%s where date between %s and %s",(record.id,record.criteria_2,record.criteria_3,))
                    else :
                        cr.execute("UPDATE tms_picking_report2_line set report_id=%s where date=%s",(record.id,record.criteria_2,))
                else :
                    cr.execute("UPDATE tms_picking_report2_line set report_id=%s where date is not null",(record.id,))
            elif record.criteria_1 == 'unused':
                if record.criteria_2:
                    cr.execute("UPDATE tms_picking_report2_line set report_id=%s where date<>%s or date is null",(record.id,record.criteria_2,)) 
                else :
                    cr.execute("UPDATE tms_picking_report2_line set report_id=%s where date is null",(record.id,))
            else :
                if record.criteria_2 :
                    #ne retourner ni le client ,ni le trajet , ni l'état des vehicles non programmés à date préciser
                    #and vehicle_id in (select vehicle_id from tms_picking where date=%s)
                    cr.execute("delete from tms_picking_report2_line where date<>%s and vehicle_id in (select vehicle_id from tms_picking where date=%s)",(record.criteria_2,record.criteria_2,))
                    cr.execute("UPDATE tms_picking_report2_line set date=null,partner_id=null,product_id=null,state=null where date<>%s",(record.criteria_2,))
                sql3 = """
                       DELETE FROM tms_picking_report2_line WHERE id NOT IN (
                       SELECT max(id) FROM tms_picking_report2_line
                       GROUP BY vehicle_id
                       ) and date is null
                       """
                #requete à mettre à jour
                cr.execute(sql3,(record.criteria_2,))
                cr.execute("UPDATE tms_picking_report2_line set report_id=%s",(record.id,))  
        self.write(cr,uid,record.id,{'count':len(record.data_line_ids)})
        return self.pool['report'].get_action(cr,uid,ids,'tms.picking_report2')


class tms_picking_report_driver_line(osv.osv_memory):
    _name = 'tms.picking.report.driver.line'
    _columns = {
            'product_id' : fields.many2one('product.product','Trajet'),
            'date' : fields.date('Date'),
            'origin' :fields.char('Num. TC'),
            'partner_id' : fields.many2one('res.partner','Client'),
            'driver_id' : fields.many2one('hr.employee','Chauffeur'),
            'driver_travel_costs' : fields.float('Frais déplacement'),
            'commission' :fields.float('Commission'),
            'report_id' : fields.many2one('tms.picking.report.driver','Report'),
    }
class tms_picking_report_driver(osv.osv_memory):
    _name = 'tms.picking.report.driver'
    
    _columns = {
        'criteria_1': fields.date("De :",required=True),
        'criteria_2' : fields.date("À :",required=True),
        'driver_id' :  fields.many2one('hr.employee','Chauffeur',domain="[('driver_ok','=',True)]"),
        'commission_move' : fields.boolean('Déplacement et Commission'),
        'data_line_ids' : fields.one2many('tms.picking.report.driver.line','report_id','Lignes'),
    }

    @api.depends('data_line_ids')
    def get_total_amount_move(self):
        amount = 0.0
        for line in self.data_line_ids:
            amount += line.driver_travel_costs
        return amount

    @api.depends('data_line_ids')
    def get_total_amount_commission(self):
        amount = 0.0
        for line in self.data_line_ids:
            amount += line.commission
        return amount

    @api.depends('data_line_ids')
    def get_total_amount(self):
        return self.get_total_amount_move() + self.get_total_amount_commission()

    def print_report(self, cr, uid, ids, data, context=None):
        cr.execute('DELETE from tms_picking_report_driver_line;')
        cr.execute("ALTER SEQUENCE tms_picking_report_driver_line_id_seq RESTART WITH 1;")
        for record in self.browse(cr,uid,ids):
            if record.driver_id:
                sql = """ 
                  INSERT INTO tms_picking_report_driver_line(product_id,date,origin,partner_id,driver_id,driver_travel_costs,commission) 
                    select product_id,date,origin,partner_id,driver_id,sum(driver_travel_costs),sum(commission)
                    from tms_picking 
                        where driver_id=%s and date between %s and %s  
                        group by driver_id,product_id,date,origin,partner_id
                        order by date
                      ;
                """
                cr.execute(sql,(record.driver_id.id,record.criteria_1,record.criteria_2,))
            else :
                sql = """ 
                  INSERT INTO tms_picking_report_driver_line(product_id,date,origin,partner_id,driver_id,driver_travel_costs,commission) 
                    select product_id,date,origin,partner_id,driver_id,sum(driver_travel_costs),sum(commission)
                    from tms_picking 
                        where date between %s and %s
                        group by driver_id,product_id,date,origin,partner_id
                      ;
                """
                cr.execute(sql,(record.criteria_1,record.criteria_2,))
            cr.execute('update tms_picking_report_driver_line set create_uid=%s,write_uid=%s',(uid,uid,))
            cr.execute("UPDATE tms_picking_report_driver_line set report_id=%s",(record.id,))
        return self.pool['report'].get_action(cr,uid,ids,'tms.picking_report_driver')

 
 

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
