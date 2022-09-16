# -*- coding:utf-8 -*-
from odoo import _, api, fields, models, tools

class UnitGuestStage(models.Model):
    _name = 'unit.guest.stages'
    _description = 'Unit Guest Stage'
    _inherits = {'project.task.type': 'stage_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']


    def _get_default_unit_ids(self):
        default_unit_id = self.env.context.get('default_unit_id')
        return [default_unit_id] if default_unit_id else None


    stage_id = fields.Many2one('project.task.type',string="Task", auto_join=True,
        required=True, readonly=True, ondelete='cascade',
        check_company=True)
    unit_ids = fields.Many2many('unit.unit', 'unit_guest_stage_rel', 'stage_id', 'unit_id', string='Units',
        default=_get_default_unit_ids)
