# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt
from odoo.exceptions import UserError, ValidationError, AccessError
from ast import literal_eval



class ProductTemplate(models.Model):
    _inherit = 'product.template'


    unit_id = fields.Many2one(
        'unit.unit', 'Unit', company_dependent=True,
        help='Select a billable unit on which guest can be created. This setting must be set for each company.',
 
    )
        
        
     
    unit_template_id = fields.Many2one(
        'unit.unit', 'Unit Template', company_dependent=True, copy=True,
        domain="[('company_id', '=', current_company_id)]",
        help='Select a billable unit to be the skeleton of the new created project when selling the current product. Its stages and guest will be duplicated.')

    @api.onchange('unit_id')
    def onchange_unit_id(self):
        self.project_id =  self.unit_id.project_id.id
    
    # @api.onchange('project_id')
    # def onchange_project_id(self):
    #     self.unit_id = self.env['unit.unit'].search([('project_id','=',self.project_id.id)]).id



class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('service_tracking')
    def _onchange_service_tracking(self):
        res = super(ProductProduct,self)._onchange_service_tracking()
        if self.service_tracking == 'no':
            self.project_id = False
            self.unit_id = False
            self.project_template_id = False
            self.unit_template_id = False
        elif self.service_tracking == 'task_global_project':
            self.project_template_id = False
            self.unit_template_id = False
        elif self.service_tracking in ['task_in_project', 'project_only']:
            self.project_id = False
            self.unit_id = False
