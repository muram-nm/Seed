# -*- coding: utf-8 -*-

import base64
from odoo.tools.image import image_data_uri
import werkzeug
import werkzeug.exceptions
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools.safe_eval import safe_eval
from odoo.tools.sql import column_exists, create_column



class ReceptionCustomer(models.Model):
	_inherit = 'reception.customer'

	guest_ids = fields.One2many('unit.guest','customer_id',string="Guests")
	total_guests = fields.Integer(compute='compute_total')
	total_forms = fields.Integer(compute='compute_total')
	total_tests = fields.Integer(compute='compute_total')
	total_treatmentplans = fields.Integer(compute='compute_total')
	total_prescriptions = fields.Integer(compute='compute_total')
	order_ids = fields.One2many('reception.order','customer_id')
	intakeform_ids = fields.One2many('unit.intakeform','customer_id')
	relative_ids = fields.One2many('reception.relative','customer_id')
	labtest_ids = fields.One2many('unit.labtest','customer_id')
	treatmentplan_ids = fields.One2many('unit.treatmentplan','customer_id')


	def compute_total(self):
		for rec in self:
			rec.total_guests = len(rec.guest_ids)
			rec.total_forms = len(rec.intakeform_ids)
			rec.total_tests = len(rec.labtest_ids)
			rec.total_treatmentplans = len(rec.treatmentplan_ids)
			rec.total_prescriptions = self.env['unit.prescription'].search_count([
				('guest_id.customer_id','=',rec.id)])

	def action_view_guests(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': _('Guests'),
			'res_model': 'unit.guest',
			'view_mode': 'list',
			'search_view_id': self.env.ref('nm_treatment_unit.view_guest_search_form').id,
			'domain': [('customer_id', '=', self.id)],
			'context':{'edit': 0,'create':0}
		}

	def action_view_prescriptions(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': _('Prescriptions'),
			'res_model': 'unit.prescription',
			'view_mode': 'list,pivot,graph',
			'search_view_id': self.env.ref('nm_reception_treatment_unit.prescription_tree_view').id,
			'domain': [('guest_id.customer_id', '=', self.id)],
			'context':{'create':0,'edit':0}
		}

	def action_get_intake_form(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': _('Intake Form'),
			'res_model': 'unit.intakeform',
			'view_mode': 'list,form',
			'domain': [('customer_id', '=', self.id)],
			'context':{'default_customer_id': self.id,'create':0},
		}

	def action_view_tests(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': _('Lab Tests'),
			'res_model': 'unit.labtest',
			'view_mode': 'list,form',
			'domain': [('customer_id', '=', self.id)],
			'context':{'default_customer_id': self.id,'create':0},
		}

	def action_view_treatmentplans(self):
		self.ensure_one()
		return {
			'type': 'ir.actions.act_window',
			'name': _('Treatment Plans'),
			'res_model': 'unit.treatmentplan',
			'view_mode': 'list,form',
			'domain': [('customer_id', '=', self.id)],
			'context':{'default_customer_id': self.id,'create':0},
		}

	# guests_ids = fields.One2many('unit.guest', 'partner_id',string='Customer')

	# def action_view_guest(self):
	#     self.ensure_one()

	#     list_view_id = self.env.ref('nm_treatment_unit.view_guest_tree2').id
	#     form_view_id = self.env.ref('nm_treatment_unit.view_guest_form2').id

	#     action = {'type': 'ir.actions.act_window_close'}
	#     guest_units = self.guests_ids.mapped('unit_id')
	#     if len(guest_units) == 1 and len(self.guests_ids) > 1:  # redirect to guest of the project (with kanban stage, ...)
	#         action = self.with_context(active_id=guest_units.id).env['ir.actions.actions']._for_xml_id(
	#             'nm_treatment_unit.act_unit_unit_2_unit_guest_all')
	#         action['domain'] = [('id', 'in', self.guests_ids.ids)]
	#         if action.get('context'):
	#             eval_context = self.env['ir.actions.actions']._get_eval_context()
	#             eval_context.update({'active_id': guest_units.id})
	#             action_context = safe_eval(action['context'], eval_context)
	#             action_context.update(eval_context)
	#             action['context'] = action_context
	#     else:
	#         action = self.env["ir.actions.actions"]._for_xml_id("nm_treatment_unit.action_view_guest")
	#         action['context'] = {}  # erase default context to avoid default filter
	#         if len(self.guests_ids) > 1:  # cross unit kanban guest
	#             action['views'] = [[False, 'kanban'], [list_view_id, 'tree'], [form_view_id, 'form'], [False, 'graph'], [False, 'calendar'], [False, 'pivot']]
	#         elif len(self.guests_ids) == 1:  # single guest -> form view
	#             action['views'] = [(form_view_id, 'form')]
	#             action['res_id'] = self.guests_ids.id
	#     # filter on the guest of the current SO
	#     action.setdefault('context', {})
	#     action['context'].update({'search_default_reception_order_id': self.id})
	#     return action