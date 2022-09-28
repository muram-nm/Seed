# -*- coding:utf-8 -*-
from odoo import api, fields, models, _

class TreatmentPlans(models.Model):
	_name = 'unit.treatmentplan'
	_description = 'Treatment Plans'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'treatmentplan_id' 

	date = fields.Date(default=fields.Date.today(),required=True)
	customer_id = fields.Many2one('reception.customer')
	guest_id = fields.Many2one('unit.guest')
	treatmentplan_id = fields.Many2one('product.product',required=True,
						tracking=True,string="Treatment")
	description = fields.Text(tracking=True)
	order_id = fields.Many2one('reception.order',string="Order")
	
	additional_comment = fields.Text(tracking=True)
	frequency = fields.Text(tracking=True)
	session_duration = fields.Float(tracking=True)
	plan_duration = fields.Float(tracking=True)
	purpose = fields.Text(tracking=True)