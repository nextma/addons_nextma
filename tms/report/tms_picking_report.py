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


class tms_picking_report(osv.osv):
    _name = 'tms.picking.report'
    _order = 'date desc'
    _auto = False
    _columns = {
            'id' : fields.integer('ID'),
            'vehicle_id' : fields.many2one('fleet.vehicle', 'Véhicle'),
            'product_id' : fields.many2one('product.product', 'Trajet'),
            'partner_id' : fields.many2one('res.partner', 'Client'),
            'date' : fields.datetime('Date'),
            }

    def _insert(self):
        insert_str = """
             INSERT INTO tms_picking_report(vehicle_id,product_id,partner_id,date) 
                    select fv.id,
                    tp.product_id,
                    tp.partner_id,
                    tp.date 
        """
        return insert_str

    def _from(self):
        from_str = """
                fleet_vehicle fv
                      left join tms_picking tp on (fv.id=tp.vehicle_id)
        """
        return from_str

    def _group_by(self):
        group_by_str = """
            GROUP BY 
                     fv.id,
                     tp.partner_id,
                     tp.product_id,
                     tp.date
        """
        return group_by_str

    def init(self, cr):
        # self._table = sale_report
        #tools.drop_view_if_exists(cr, self._table)
        cr.execute('select * from ir_model where model=%s',('tms.picking.report',))
        ir_model_id = cr.fetchall()
        print ir_model_id
        if ir_model_id:
            print "#####################################################"
            cr.execute('DROP TABLE tms_picking_report;')
            cr.execute('delete from ir_model where model=%s',('tms.picking.report',))
        cr.execute("""
        CREATE TABLE tms_picking_report
            (
          id serial NOT NULL,
          vehicle_id integer,
          product_id integer,
          partner_id integer,
          date timestamp without time zone,
          CONSTRAINT tms_picking_report_pkey PRIMARY KEY (id)
            );
           """)
        cr.execute("""
            %s
            FROM (%s)
            """ % (self._insert(),self._from()))

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
