# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models

class UnitGuestStagePersonal(models.Model):
    _name = 'unit.guest.stage.personal'
    _description = 'Personal Guest Stage'
    # _table = 'unit_guest_user_rel'
    # _rec_name = 'stage_id'
    _inherits = {'project.task.stage.personal': 'personal_stage_id'}

    personal_stage_id = fields.Many2one('project.task.stage.personal',string="Personal Stage", auto_join=True,
        required=True, readonly=True, ondelete='cascade',
        check_company=True)
    guest_id = fields.Many2one('unit.guest', required=True, ondelete='cascade', index=True)
    