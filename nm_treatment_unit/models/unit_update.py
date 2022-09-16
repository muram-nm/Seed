# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta
from dateutil.relativedelta import relativedelta
from werkzeug.urls import url_encode

from odoo import api, fields, models
from odoo.osv import expression
from odoo.tools import formatLang

class TreatmentUpdate(models.Model):
    _name = 'unit.update'
    _description = 'Unit Update'
    _order = 'date desc'
    _inherits = {'project.update': 'update_id'}
    _inherit = ['mail.thread.cc', 'mail.activity.mixin']

    unit_id = fields.Many2one('unit.unit', required=True)
    update_id = fields.Many2one('project.update',string="Task", auto_join=True,
        required=True, readonly=True, ondelete='cascade',
        check_company=True)
