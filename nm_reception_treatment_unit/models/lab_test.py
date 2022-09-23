# -*- coding:utf-8 -*-
from odoo import api, fields, models, _

class LabTest(models.Model):
	_name = 'lab.test'
	_description = 'Lab Test'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'sequence' 


	sequence = fields.Char(readonly=True,tracking=True)
	date = fields.Date(default=fields.Date.today(),tracking=True,required="1")
	lab_test_type = fields.Many2one('product.template',required=True,
						tracking=True,domain="[('reception_ok','=',True)]")
	customer_id = fields.Many2one('reception.customer',string="Customer",tracking=True)
	guest_id = fields.Many2one('unit.guest',string="Guest",tracking=True)
	test_id = fields.Many2one('product.product',required=True,
						tracking=True,domain="[('reception_ok','=',True)]")
	description = fields.Text(tracking=True)
	result = fields.Text(tracking=True)
	normal_range = fields.Text(tracking=True)
	sample_type = fields.Text(tracking=True)
	order_id = fields.Many2one('reception.order',string="Order")
	is_paid = fields.Boolean(tracking=True,readonly=True)
	is_added = fields.Boolean()
	note = fields.Text()


	@api.model
	def create(self, vals):
		vals['sequence'] = self.env['ir.sequence'].next_by_code('lab.test') or '/'
		res = super(LabTest, self).create(vals)
		return res