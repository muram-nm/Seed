# -*- coding:utf-8 -*-
from odoo import _, api, fields, models, tools

class UnitGuestStage(models.Model):
    _name = 'unit.guest.stages'
    _description = 'Unit Guest Stage'
    _inherits = {'project.task.type': 'stage_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']


    intake_form = fields.Boolean("Intake Form")
    consent_for = fields.Boolean("Consent Form")
    vital_signs = fields.Boolean("Vital Signs")
    assessments = fields.Boolean("Assessments")
    lab_test = fields.Boolean("Lab Test")
    prescription = fields.Boolean("Prescription")
    treatment_plan = fields.Boolean("Treatment Plan")   
    description_page = fields.Boolean("Description")  
    user_ids = fields.Many2many('res.users',string='Users')
    capacity = fields.Integer('Capacity')

    def _get_default_unit_ids(self):
        default_unit_id = self.env.context.get('default_unit_id')
        return [default_unit_id] if default_unit_id else None


    stage_id = fields.Many2one('project.task.type',string="Task", auto_join=True,
        required=True, readonly=True, ondelete='cascade',
        check_company=True)
    unit_ids = fields.Many2many('unit.unit', 'unit_guest_stage_rel', 'stage_id', 'unit_id', string='Units',
        default=_get_default_unit_ids)

    def unlink_wizard(self, stage_view=False):
        self = self.with_context(active_test=False)
        # retrieves all the units with a least 1 guest in that stage
        # a guest can be in a stage even if the unit is not assigned to the stage
        readgroup = self.with_context(active_test=False).env['unit.guest'].read_group([('stage_id', 'in', self.ids)], ['project_id'], ['project_id'])
        unit_ids = list(set([unit['unit_id'][0] for unit in readgroup] + self.unit_ids.ids))

        wizard = self.with_context(unit_ids=unit_ids).env['unit.guest.stages.delete.wizard'].create({
            'unit_ids': unit_ids,
            'stage_ids': self.ids
        })

        context = dict(self.env.context)
        context['stage_view'] = stage_view
        return {
            'name': _('Delete Stage'),
            'view_mode': 'form',
            'res_model': 'unit.guest.stages.delete.wizard',
            'views': [(self.env.ref('nm_treatment_unit.view_unit_guest_stage_delete_wizard').id, 'form')],
            'type': 'ir.actions.act_window',
            'res_id': wizard.id,
            'target': 'new',
            'context': context,
        }