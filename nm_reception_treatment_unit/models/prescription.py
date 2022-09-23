# -*- coding:utf-8 -*-
from odoo import api, fields, models, _

class Prescription(models.Model):
	_name = 'prescription.prescription'
	_description = 'Prescription'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'prescription_id' 

	date = fields.Date(default=fields.Date.today(),required=True)
	customer_id = fields.Many2one('reception.customer')
	guest_id = fields.Many2one('unit.guest')
	prescription_id = fields.Many2one('product.product',required=True,
						tracking=True)
	description = fields.Text(tracking=True)
	order_id = fields.Many2one('reception.order',string="Order")
						