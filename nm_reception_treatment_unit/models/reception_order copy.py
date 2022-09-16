# -*- coding:utf-8 -*-
from odoo import api, fields, models, _

from odoo.tools.safe_eval import safe_eval
from odoo.tools.sql import column_exists, create_column



class ReceptionOrder(models.Model):
    _inherit = 'reception.order'

    guests_ids = fields.Many2many('unit.guest', compute='_compute_guests_ids', string='Guests associated to this sale')
    guests_count = fields.Integer(string='Guests', compute='_compute_guests_ids', groups="nm_treatment_unit.group_unit_user")
    # visible_unit = fields.Boolean('Display Unit', compute='_compute_visible_unit', readonly=True)
    unit_id = fields.Many2one(
        'unit.unit', 'Unit', readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]},
        help='Select a non billable Unit on which guests can be created.')
    unit_ids = fields.Many2many('unit.unit', compute="_compute_unit_ids", string='Unit', copy=False, groups="nm_treatment_unit.group_unit_manager", help="units used in this sales order.")
    # unit_count = fields.Integer(string='Number of Units', compute='_compute_project_ids', groups='project.group_project_manager')
  


  
    @api.depends('order_line.product_id.unit_id')
    def _compute_guests_ids(self):
        for order in self:
            order.guests_ids = self.env['unit.guest'].search(['|', ('reception_order_id', 'in', order.order_line.ids), ('reception_order_id', '=', order.id)])
            order.guests_count = len(order.guests_ids)

    
    # @api.depends('order_line.product_id.service_tracking')
    # def _compute_visible_unit(self):
    #     """ Users should be able to select a unit_id on the SO if at least one SO line has a product with its service tracking
    #     configured as 'task_in_project' """
    #     for order in self:
    #         order.visible_unit = any(
    #             service_tracking == 'task_in_project' for service_tracking in order.order_line.mapped('product_id.service_tracking')
    #         )


    @api.depends('order_line.product_id', 'order_line.unit_id')
    def _compute_unit_ids(self):
        for order in self:
            units = order.order_line.mapped('product_id.unit_id')
            units |= order.order_line.mapped('unit_id')
            units |= order.unit_id
            order.unit_ids = units
            # order.unit_count = len(units)


 

    @api.onchange('unit_id')
    def _onchange_unit_id(self):
        """ Set the SO analytic account to the selected project's analytic account """
        if self.unit_id.analytic_account_id:
            self.analytic_account_id = self.unit_id.analytic_account_id


    def action_view_guest(self):
        self.ensure_one()

        list_view_id = self.env.ref('nm_treatment_unit.view_guest_tree2').id
        form_view_id = self.env.ref('nm_treatment_unit.view_guest_form2').id

        action = {'type': 'ir.actions.act_window_close'}
        guest_units = self.guests_ids.mapped('unit_id')
        if len(guest_units) == 1 and len(self.guests_ids) > 1:  # redirect to guest of the project (with kanban stage, ...)
            action = self.with_context(active_id=guest_units.id).env['ir.actions.actions']._for_xml_id(
                'nm_treatment_unit.act_unit_unit_2_unit_guest_all')
            action['domain'] = [('id', 'in', self.guests_ids.ids)]
            if action.get('context'):
                eval_context = self.env['ir.actions.actions']._get_eval_context()
                eval_context.update({'active_id': guest_units.id})
                action_context = safe_eval(action['context'], eval_context)
                action_context.update(eval_context)
                action['context'] = action_context
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("nm_treatment_unit.action_view_guest")
            action['context'] = {}  # erase default context to avoid default filter
            if len(self.guests_ids) > 1:  # cross unit kanban guest
                action['views'] = [[False, 'kanban'], [list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot']]
            elif len(self.guests_ids) == 1:  # single guest -> form view
                action['views'] = [(form_view_id, 'form')]
                action['res_id'] = self.guests_ids.id
        # filter on the guest of the current SO
        action.setdefault('context', {})
        action['context'].update({'search_default_reception_order_id': self.id})
        return action

    def action_view_unit_ids(self):
        self.ensure_one()
        view_form_id = self.env.ref('nm_treatment_unit.edit_unit').id
        view_kanban_id = self.env.ref('nm_treatment_unit.view_unit_kanban').id
        action = {
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.unit_ids.ids)],
            'views': [(view_kanban_id, 'kanban'), (view_form_id, 'form')],
            'view_mode': 'kanban,form',
            'name': _('Units'),
            'res_model': 'unit.unit',
        }
        return action

    def write(self, values):
        if 'state' in values and values['state'] == 'cancel':
            self.unit_id.sale_line_id = False
        return super(ReceptionOrder, self).write(values)



    def _action_confirm(self):
        """ On SO confirmation, some lines should generate a task or a project. """
        result = super()._action_confirm()
        if self.order_line:
          
            for line in self.order_line:
                if line.product_id.detaild_type == 'service' and line.product_id.service_tracking == 'task_global_project' and line.product_id.unit_id: 
                    unit = self.env['unit.unit'].search([('project_id','=',self.project_id.id)])
                    if unit:
                        x = self.env['unit.guest'].create({
                            'name':self.name,
                            'unit_id':unit.id
                        })

           
        if len(self.company_id) == 1:
            # All orders are in the same company
            self.order_line.sudo().with_company(self.company_id)._timesheet_service_generation()
        else:
            # Orders from different companies are confirmed together
            for order in self:
                order.order_line.sudo().with_company(order.company_id)._timesheet_service_generation()
        return result


   

