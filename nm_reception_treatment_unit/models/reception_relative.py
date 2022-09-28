# -*- coding: utf-8 -*-

from odoo import api, models, fields, _


class ReceptionRelatives(models.Model):
	_name = 'reception.relative'
	_description = 'Reception Relatives'
	_inherit = ['mail.thread', 'mail.activity.mixin']

	name = fields.Char(required=True,tracking=True)
	date_of_birth = fields.Date('Date of Birth', required=True, tracking=True)
	age = fields.Integer(compute='_compute_age', store=True, tracking=True)
	is_adult = fields.Boolean(compute='_compute_adult',store=True, tracking=True)
	relation = fields.Selection([
		('father','Father'),('mother','Mother'),
		('brother','Brother'),('sister','Sister'),
		('son','Son'),('daughter','Daughter'),
		('spouse','Spouse')],tracking=True,required=True)
	medical_history = fields.Text(tracking=True)
	customer_id = fields.Many2one('reception.customer')

	@api.depends('date_of_birth')
	def _compute_age(self):
		today = fields.Date.today()
		for relative in self:
			relative.age = relative.date_of_birth and int((today - relative.date_of_birth).days / 365.2425)


	@api.depends('age')
	def _compute_adult(self):
		for relative in self:
			relative.is_adult = False
			if relative.age >= 18:
				relative.is_adult = True
