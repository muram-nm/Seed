# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

import ast


class ProjectTaskTypeDelete(models.TransientModel):
    _name = 'unit.guest.stages.delete.wizard'
    _description = 'Guest Stage Delete Wizard'

    unit_ids = fields.Many2many('unit.unit', domain="['|', ('active', '=', False), ('active', '=', True)]", string='Units', ondelete='cascade')
    stage_ids = fields.Many2many('unit.guest.stages', string='Stages To Delete', ondelete='cascade')
    guests_count = fields.Integer('Number of Guests', compute='_compute_guests_count')
    stages_active = fields.Boolean(compute='_compute_stages_active')

    @api.depends('unit_ids')
    def _compute_guests_count(self):
        for wizard in self:
            wizard.guests_count = self.with_context(active_test=False).env['unit.guest'].search_count([('stage_id', 'in', wizard.stage_ids.ids)])

    @api.depends('stage_ids')
    def _compute_stages_active(self):
        for wizard in self:
            wizard.stages_active = all(wizard.stage_ids.mapped('active'))

    def action_archive(self):
        if len(self.unit_ids) <= 1:
            return self.action_confirm()

        return {
            'name': _('Confirmation'),
            'view_mode': 'form',
            'res_model': 'unit.guest.stages.delete.wizard.wizard',
            'views': [(self.env.ref('project.view_project_task_type_delete_confirmation_wizard').id, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context': self.env.context,
        }

    def action_confirm(self):
        tasks = self.with_context(active_test=False).env['unit.guest'].search([('stage_id', 'in', self.stage_ids.ids)])
        tasks.write({'active': False})
        self.stage_ids.write({'active': False})
        return self._get_action()

    def action_unlink(self):
        self.stage_ids.unlink()
        return self._get_action()

    def _get_action(self):
        unit_id = self.env.context.get('default_unit_id')

        if unit_id:
            action = self.env["ir.actions.actions"]._for_xml_id("nm_treatment_unit.action_view_guest")
            action['domain'] = [('unit_id', '=', unit_id)]
            action['context'] = str({
                'pivot_row_groupby': ['user_ids'],
                'default_unit_id': unit_id,
            })
        elif self.env.context.get('stage_view'):
            action = self.env["ir.actions.actions"]._for_xml_id("nm_treatment_unit.open_guest_type_form")
        else:
            action = self.env["ir.actions.actions"]._for_xml_id("nm_treatment_unit.action_view_all_guest")

        context = dict(ast.literal_eval(action.get('context')), active_test=True)
        action['context'] = context
        action['target'] = 'main'
        return action
