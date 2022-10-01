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


class Guest(models.Model):
    _name = 'unit.guest'
    _description = 'Treatment Guests'
    _inherits = {'project.task': 'task_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']

    
    def _get_default_stage_id(self):
        """ Gives default stage_id """
        unit_id = self.env.context.get('default_unit_id')
        if not unit_id:
            return False
        return self.stage_find(unit_id, [('fold', '=', False), ('is_closed', '=', False)])

    @api.model
    def _default_company_id(self):
        if self._context.get('default_unit_id'):
            return self.env['unit.unit'].browse(self._context['default_unit_id']).company_id
        return self.env.company



    @api.model
    def _get_default_partner_id(self, unit=None, parent=None):
        if parent and parent.partner_id:
            return parent.partner_id.id
        if unit and unit.partner_id:
            return unit.partner_id.id
        return False


    active = fields.Boolean(default=True)
    task_id = fields.Many2one('project.task',string="Task", auto_join=True,
        readonly=True, ondelete='cascade',
        check_company=True)
    display_unit_id = fields.Many2one('unit.unit', index=True)
    unit_id = fields.Many2one('unit.unit', string='Unit',
        compute='_compute_unit_id', recursive=True, store=True, readonly=False,
        index=True, tracking=True, check_company=True, change_default=True)
    dependent_guest_count = fields.Integer(string="Dependent Guests", compute='_compute_dependent_guest_count')
    parent_id = fields.Many2one('unit.guest', string='Parent Guest', index=True)
    personal_stage_id = fields.Many2one('unit.guest.stage.personal', string='Personal Stage State', compute_sudo=False,
        compute='_compute_personal_stage_id', help="The current user's personal stage.")
    personal_stage_type_ids = fields.Many2many('unit.guest.stages', 'unit_guest_user_rel', column1='guest_id', column2='stage_id',
        ondelete='restrict', group_expand='_read_group_personal_stage_type_ids', copy=False,
        domain="[('user_id', '=', user.id)]", depends=['user_ids'], string='Personal Stage')
    personal_stage_type_id = fields.Many2one('unit.guest.stages', string='Personal User Stage',
        compute='_compute_personal_stage_type_id', inverse='_inverse_personal_stage_type_id', store=False,
        search='_search_personal_stage_type_id',
        help="The current user's personal task stage.")
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
        index=True,
        copy=False,
        readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False, tracking=True, task_dependency_tracking=True)
    priority = fields.Selection([
            ('0', 'Normal'),
            ('1', 'Important'),
        ], default='0', index=True, string="Starred", tracking=True)
    is_private = fields.Boolean(compute='_compute_is_private')
    stage_id = fields.Many2one('unit.guest.stages', string='Stage', compute='_compute_stage_id',
        store=True, readonly=False, ondelete='restrict', tracking=True, index=True,
        default=_get_default_stage_id, group_expand='_read_group_stage_ids',
        domain="[('unit_ids', '=', unit_id)]", copy=False, task_dependency_tracking=True)
    kanban_state = fields.Selection([
        ('normal', 'In Progress'),
        ('done', 'Ready'),
        ('blocked', 'Blocked')], string='Status',
        copy=False, default='normal', required=True)
    company_id = fields.Many2one(
        'res.company', string='Company', compute='_compute_company_id', store=True, readonly=False,
        required=True, copy=True, default=_default_company_id)
    partner_id = fields.Many2one('res.partner', string='Customer', auto_join=True, tracking=True, domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]")
    blood_pressure = fields.Char('Blood Pressure')
    templerature = fields.Char('Templerature')
    heat_rate = fields.Char('Heat Rate')
    respiratoy_rate = fields.Char('Respiratoy Rate')
    spo = fields.Char('SPO 2%')


    @api.depends('unit_id.company_id')
    def _compute_company_id(self):
        for task in self.filtered(lambda task: task.unit_id):
            task.company_id = task.unit_id.company_id



    @api.depends('parent_id', 'unit_id', 'display_unit_id')
    def _compute_partner_id(self):
        """ Compute the partner_id when the tasks have no partner_id.

            Use the unit partner_id if any, or else the parent task partner_id.
        """
        for guest in self.filtered(lambda guest: not guest.partner_id):
            # When the task has a parent task, the display_unit_id can be False or the project choose by the user for this task.
            unit = guest.display_unit_id if guest.parent_id and guest.display_unit_id else guest.unit_id
            guest.partner_id = self._get_default_partner_id(unit, guest.parent_id)



    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_unit_id' in self.env.context:
            search_domain = ['|', ('unit_ids', '=', self.env.context['default_unit_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)




    @api.depends('unit_id', 'parent_id')
    def _compute_is_private(self):
        # Modify accordingly, this field is used to display the lock on the guest's kanban card
        for guest in self:
            guest.is_private = not guest.unit_id and not guest.parent_id


    @api.model
    def _read_group_personal_stage_type_ids(self, stages, domain, order):
        return stages.search(['|', ('id', 'in', stages.ids), ('user_id', '=', self.env.user.id)])


    @api.depends('personal_stage_id')
    def _compute_personal_stage_type_id(self):
        for guest in self:
            guest.personal_stage_type_id = guest.personal_stage_id.stage_id

    def _inverse_personal_stage_type_id(self):
        for guest in self:
            guest.personal_stage_id.stage_id = guest.personal_stage_type_id

    @api.model
    def _search_personal_stage_type_id(self, operator, value):
        return [('personal_stage_type_ids', operator, value)]


    @api.depends_context('uid')
    @api.depends('user_ids')
    def _compute_personal_stage_id(self):
        # An user may only access his own 'personal stage' and there can only be one pair (user, guest_id)
        personal_stages = self.env['unit.guest.stage.personal'].search([('user_id', '=', self.env.uid), ('guest_id', 'in', self.ids)])
        self.personal_stage_id = False
        for personal_stage in personal_stages:
            personal_stage.guest_id.personal_stage_id = personal_stage


    @api.depends('dependent_ids')
    def _compute_dependent_guest_count(self):
        guests_with_dependency = self.filtered('allow_guest_dependencies')
        (self - guests_with_dependency).dependent_guest_count = 0
        if guests_with_dependency:
            group_dependent = self.env['unit.guest'].read_group([
                ('depend_on_ids', 'in', guests_with_dependency.ids),
            ], ['depend_on_ids'], ['depend_on_ids'])
            dependent_guests_count_dict = {
                group['depend_on_ids'][0]: group['depend_on_ids_count']
                for group in group_dependent
            }
            for guest in guests_with_dependency:
                guest.dependent_guests_count = dependent_guests_count_dict.get(guest.id, 0)


    @api.depends('parent_id.unit_id', 'display_unit_id')
    def _compute_unit_id(self):
        for guest in self:
            if guest.parent_id:
                guest.unit_id = guest.display_unit_id or guest.parent_id.unit_id

    
    def action_dependent_guest(self):
        self.ensure_one()
        action = {
            'res_model': 'unit.guest',
            'type': 'ir.actions.act_window',
            'context': {**self._context, 'default_depend_on_ids': [Command.link(self.id)], 'show_treatment_update': False},
            'domain': [('depend_on_ids', '=', self.id)],
        }
        if self.dependent_guest_count == 1:
            action['view_mode'] = 'form'
            action['res_id'] = self.dependent_ids.id
            action['views'] = [(False, 'form')]
        else:
            action['name'] = _('Dependent Guest')
            action['view_mode'] = 'tree,form,kanban,calendar,pivot,graph,activity'
        return action

    def action_assign_to_me(self):
        self.write({'user_ids': [(4, self.env.user.id)]})

    def action_open_parent_guest(self):
        return {
            'name': _('Parent Guest'),
            'view_mode': 'form',
            'res_model': 'unit.guest',
            'res_id': self.parent_id.id,
            'type': 'ir.actions.act_window',
            'context': self._context
        }

    @api.depends('unit_id')
    def _compute_stage_id(self):
        for guest in self:
            if guest.unit_id:
                if guest.unit_id not in guest.stage_id.unit_ids:
                    guest.stage_id = guest.stage_find(guest.unit_id.id, [
                        ('fold', '=', False), ('is_closed', '=', False)])
            else:
                guest.stage_id = False


    @api.model_create_multi
    def create(self, vals_list):
        is_portal_user = self.env.user.has_group('base.group_portal')
        if is_portal_user:
            self.check_access_rights('create')
        default_stage = dict()
        for vals in vals_list:
            if is_portal_user:
                self._ensure_fields_are_accessible(vals.keys(), operation='write', check_group_user=False)

            unit_id = vals.get('unit_id') or self.env.context.get('default_unit_id')
            if unit_id and not "company_id" in vals:
                vals["company_id"] = self.env["unit.unit"].browse(
                    unit_id
                ).company_id.id or self.env.company.id
            if unit_id and "stage_id" not in vals:
                # 1) Allows keeping the batch creation of guests
                # 2) Ensure the defaults are correct (and computed once by unit),
                # by using default get (instead of _get_default_stage_id or _stage_find),
                if unit_id not in default_stage:
                    default_stage[unit_id] = self.with_context(
                        default_unit_id=unit_id
                    ).default_get(['stage_id']).get('stage_id')
                   
                vals["stage_id"] = default_stage[unit_id]
                
            # user_ids change: update date_assign
            if vals.get('user_ids'):
                vals['date_assign'] = fields.Datetime.now()
            # Stage change: Update date_end if folded stage and date_last_stage_update
            if vals.get('stage_id'):
                vals.update(self.update_date_end(vals['stage_id']))
                vals['date_last_stage_update'] = fields.Datetime.now()
            # recurrence
            
        # The sudo is required for a portal user as the record creation
        # requires the read access on other models, as mail.template
        # in order to compute the field tracking
        
        was_in_sudo = self.env.su
        if is_portal_user:
            ctx = {
                key: value for key, value in self.env.context.items()
                if key == 'default_unit_id' \
                    or not key.startswith('default_') \
                    or key[8:] in self.SELF_WRITABLE_FIELDS
            }
            self = self.with_context(ctx).sudo()
        
        guests = super(Guest, self).create(vals_list)
        guests._populate_missing_personal_stages()
        self._guest_message_auto_subscribe_notify({guest: guest.user_ids - self.env.user for guest in guests})

        # in case we were already in sudo, we don't check the rights.
        if is_portal_user and not was_in_sudo:
            # since we use sudo to create guests, we need to check
            # if the portal user could really create the guests based on the ir rule.
            guests.with_user(self.env.user).check_access_rule('create')
        return guests

    def write(self, vals):
        portal_can_write = False
        if self.env.user.has_group('base.group_portal') and not self.env.su:
            # Check if all fields in vals are in SELF_WRITABLE_FIELDS
            self._ensure_fields_are_accessible(vals.keys(), operation='write', check_group_user=False)
            self.check_access_rights('write')
            self.check_access_rule('write')
            portal_can_write = True

        now = fields.Datetime.now()
        if 'parent_id' in vals and vals['parent_id'] in self.ids:
            raise UserError(_("Sorry. You can't set a guest as its parent guest."))
        
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals.update(self.update_date_end(vals['stage_id']))
            vals['date_last_stage_update'] = now
            # reset kanban state when changing stage
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
        # user_ids change: update date_assign
        if vals.get('user_ids') and 'date_assign' not in vals:
            vals['date_assign'] = now

       

        guests = self
        # The sudo is required for a portal user as the record update
        # requires the write access on others models, as rating.rating
        # in order to keep the same name than the guest.
        if portal_can_write:
            guests = guests.sudo()

        # Track user_ids to send assignment notifications
        old_user_ids = {t: t.user_ids for t in self}

        result = super(Guest, guests).write(vals)

        self._guest_message_auto_subscribe_notify({guest: guest.user_ids - old_user_ids[guest] - self.env.user for guest in self})

        if 'user_ids' in vals:
            guests._populate_missing_personal_stages()

        # rating on stage
        # if 'stage_id' in vals and vals.get('stage_id'):
        #     self.filtered(lambda x: x.unit_id.rating_active and x.unit_id.rating_status == 'stage')._send_guest_rating_mail(force_send=True)
        for guest in self:
            if guest.display_unit_id != guest.unit_id and not guest.parent_id:
                # We must make the display_unit_id follow the unit_id if no parent_id set
                guest.display_unit_id = guest.unit_id
        return result


    def _populate_missing_personal_stages(self):
        # Assign the default personal stage for those that are missing
        personal_stages_without_stage = self.env['unit.guest.stage.personal'].sudo().search([('guest_id', 'in', self.ids), ('stage_id', '=', False)])
        if personal_stages_without_stage:
            user_ids = personal_stages_without_stage.user_id
            personal_stage_by_user = defaultdict(lambda: self.env['unit.guest.stage.personal'])
            for personal_stage in personal_stages_without_stage:
                personal_stage_by_user[personal_stage.user_id] |= personal_stage
            for user_id in user_ids:
                stage = self.env['unit.guest.stages'].sudo().search([('user_id', '=', user_id.id)], limit=1)
                # In the case no stages have been found, we create the default stages for the user
                if not stage:
                    stages = self.env['unit.guest.stages'].sudo().with_context(lang=user_id.partner_id.lang, default_unit_id=False).create(
                        self._get_default_personal_stage_create_vals(user_id.id)
                    )
                    stage = stages[0]
                personal_stage_by_user[user_id].sudo().write({'stage_id': stage.id})

    @api.model
    def _get_default_personal_stage_create_vals(self, user_id):
        return [
            {'sequence': 1, 'name': _('Inbox'), 'user_id': user_id, 'fold': False},
            {'sequence': 2, 'name': _('Today'), 'user_id': user_id, 'fold': False},
            {'sequence': 3, 'name': _('This Week'), 'user_id': user_id, 'fold': False},
            {'sequence': 4, 'name': _('This Month'), 'user_id': user_id, 'fold': False},
            {'sequence': 5, 'name': _('Later'), 'user_id': user_id, 'fold': False},
            {'sequence': 6, 'name': _('Done'), 'user_id': user_id, 'fold': True},
            {'sequence': 7, 'name': _('Canceled'), 'user_id': user_id, 'fold': True},
        ]

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.model
    def _guest_message_auto_subscribe_notify(self, users_per_guest):
        # Utility method to send assignation notification upon writing/creation.
        template_id = self.env['ir.model.data']._xmlid_to_res_id('nm_treatment_unit.unit_message_user_assigned', raise_if_not_found=False)
        if not template_id:
            return
        view = self.env['ir.ui.view'].browse(template_id)
        guest_model_description = self.env['ir.model']._get(self._name).display_name
        for guest, users in users_per_guest.items():
            if not users:
                continue
            values = {
                'object': guest,
                'model_description': guest_model_description,
                'access_link': guest._notify_get_action_link('view'),
            }
            for user in users:
                values.update(assignee_name=user.sudo().name)
                assignation_msg = view._render(values, engine='ir.qweb', minimal_qcontext=True)
                assignation_msg = self.env['mail.render.mixin']._replace_local_links(assignation_msg)
                guest.message_notify(
                    subject=_('You have been assigned to %s', guest.display_name),
                    body=assignation_msg,
                    partner_ids=user.partner_id.ids,
                    record_name=guest.display_name,
                    email_layout_xmlid='mail.mail_notification_light',
                    model_description=guest_model_description,
                )

    # ----------------------------------------
    # Case management
    # ----------------------------------------

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('unit_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('unit_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['unit.guest.stages'].search(search_domain, order=order, limit=1).id

    def update_date_end(self, stage_id):
        unit_guest_type = self.env['unit.guest.stages'].browse(stage_id)
        if unit_guest_type.fold or unit_guest_type.is_closed:
            return {'date_end': fields.Datetime.now()}
        return {'date_end': False}