# -*- coding:utf-8 -*-
from odoo import api, fields, models, _

class Supplements(models.Model):
	_name = 'unit.prescription'

	prescription_id = fields.Many2one('product.product',tracking=True,required=True)
	purpose = fields.Text(tracking=True)
	per_day = fields.Many2one('unit.prescription.details',tracking=True)
	upon_arising = fields.Many2one('unit.prescription.details',tracking=True)
	with_breakfast = fields.Many2one('unit.prescription.details',tracking=True)
	mid_morning = fields.Many2one('unit.prescription.details',tracking=True)
	with_lunch = fields.Many2one('unit.prescription.details',tracking=True)
	mid_afternoon = fields.Many2one('unit.prescription.details',tracking=True)
	with_dinner = fields.Many2one('unit.prescription.details',tracking=True)
	prior_to_bed = fields.Many2one('unit.prescription.details',tracking=True)
	guest_id = fields.Many2one('unit.guest')



class SupplementsDetails(models.Model):
	_name = 'unit.prescription.details'

	name = fields.Text(required=True)