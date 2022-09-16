# -*- coding: utf-8 -*-
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import ast
import json
from collections import defaultdict
from datetime import timedelta, datetime
from random import randint

from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt
from odoo.exceptions import UserError, ValidationError, AccessError
from odoo.tools import format_amount
from odoo.osv.expression import OR

class TreatmentUnit(models.Model):
    _name = 'unit.unit'
    _description = 'Treatment unit'
    _inherits = {'project.project': 'project_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']



    def _default_stage_id(self):
        # Since project stages are order by sequence first, this should fetch the one with the lowest sequence number.
        return self.env['unit.guest.stages'].search([], limit=1)



    project_id = fields.Many2one('project.project',string='Project', auto_join=True,
        required=True, readonly=True, ondelete='cascade',
        check_company=True)
    # name = fields.Char(string='Name', required=True, translate=True, tracking=True)
    guest_count = fields.Integer(compute='_compute_guest_count', string="Guest Count")
    guest_count_with_subtasks = fields.Integer(compute='_compute_guest_count')
    label_guests = fields.Char(string='Use Guest as', default='Guests', help="Label used for the guests of the unit.", translate=True,tracking=True)
    description = fields.Html(tracking=True)
    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide the unit without removing it.", tracking=True)
    # stage_ids = fields.Many2many('unit.guest.stages', 'unit_guest_stage_rel', 'unit_id', 'stage_id', string='Guest Stages')
    stage_id = fields.Many2one('unit.guest.stages', string='Stage', ondelete='restrict', groups="project.group_project_stages",
        tracking=True, index=True, copy=False, default=_default_stage_id, group_expand='_read_group_stage_ids')




    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_unit_id' in self.env.context:
            search_domain = ['|', ('unit_ids', '=', self.env.context['default_unit_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)



    def action_view_guests_analysis(self):
        """ return the action to see the guests analysis report of the unit """
        action = self.env['ir.actions.act_window']._for_xml_id('nm_treatment_unit.action_unit_guest_user_tree')
        action_context = ast.literal_eval(action['context']) if action['context'] else {}
        action_context['search_default_unit_id'] = self.id
        return dict(action, context=action_context)


    def action_view_guest(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('nm_treatment_unit.act_unit_2_unit_guest_all') \
            .sudo().read()[0]
        action['display_name'] = self.name
        return action

    def _get_user_values(self):
        return {
            'is_treatment_user': self.user_has_groups('nm_treatment_unit.group_unit_user'),
        }

    def _compute_guest_count(self):
            guest_data = self.env['unit.guest'].read_group(
                [('unit_id', 'in', self.ids),
                '|',
                    ('stage_id.fold', '=', False),
                    ('stage_id', '=', False)],
                ['unit_id', 'display_unit_id:count'], ['unit_id'])
            result_wo_subguest = defaultdict(int)
            result_with_subguest = defaultdict(int)
            for data in guest_data:
                result_wo_subguest[data['unit_id'][0]] += data['display_unit_id']
                result_with_subguest[data['unit_id'][0]] += data['unit_id_count']
            for treatment in self:
                treatment.guest_count = result_wo_subguest[treatment.id]
                treatment.guest_count_with_subtasks = result_with_subguest[treatment.id]

    def action_view_kanban_unit(self):
        # [XBO] TODO: remove me in master
        return

    def action_view_guests(self):
        action = self.with_context(active_id=self.id, active_ids=self.ids) \
            .env.ref('nm_treatment_unit.act_unit_2_unit_guest_all') \
            .sudo().read()[0]
        action['display_name'] = self.name
        return action

    def action_view_guests_analysis(self):
        """ return the action to see the tasks analysis report of the unit """
        action = self.env['ir.actions.act_window']._for_xml_id('nm_treatment_unit.report_unit_guest_user_view_tree')
        action_context = ast.literal_eval(action['context']) if action['context'] else {}
        action_context['search_default_unit_id'] = self.id
        return dict(action, context=action_context)

    @api.model
    def create(self, values):
        # CODE HERE
        res = super(TreatmentUnit, self).create(values)
        if res['name']:
            res['analytic_account_id'] = self.env['account.analytic.account'].create({'name':res['name']}).id
        return res