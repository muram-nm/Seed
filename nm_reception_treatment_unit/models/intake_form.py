# -*- coding:utf-8 -*-
from odoo import api, fields, models, _

class IntakeForm(models.Model):
	_name = 'intake.form'
	_description = 'Intake Form'
	_inherit = ['mail.thread', 'mail.activity.mixin']
	_rec_name = 'partner_id' 

	partner_id = fields.Many2one('reception.customer',string="Customer",
								tracking=True)
	qid = fields.Char(related="partner_id.qid",tracking=True)
	date_of_birth = fields.Date(related="partner_id.date_of_birth",
								tracking=True)
	age = fields.Integer(related="partner_id.age",tracking=True)
	date = fields.Date(default=fields.Date.today(),string="Today's Date",
						tracking=True,readonly=True)
	email = fields.Char(related="partner_id.email",tracking=True)
	phone = fields.Char(related="partner_id.phone",string="Cell Phone",
						tracking=True)
	hear_about_us = fields.Selection([
		('ifm', 'IFM Website'),('referral_clinician', 'Referral From Clinician'),
		('referral_friend_family', 'Referral From friend/family'),('member', 'Member'),
		('google', 'Google Search'),('media', 'Social Media'),('other','Other')],
		 tracking=True)
	media = fields.Char(tracking=True)
	hear_other = fields.Char(tracking=True)
	emergency_contact = fields.Char(tracking=True)
	relationship = fields.Char(tracking=True)
	cell = fields.Char(tracking=True)
	health_concerns_ids = fields.One2many('medical.medical','form_id',
						tracking=True,
						domain=[('is_health_concerns','=',True)])
	medical_history_ids = fields.One2many('medical.medical','form_id',
						tracking=True,
						domain=[('is_medical_history','=',True)])
	customer_achieve = fields.Text(tracking=True)
	allergies_ids = fields.One2many('medical.medical','form_id',
						tracking=True,
						domain=[('is_allergies','=',True)])
	sleep_hours = fields.Char(tracking=True)
	sleep_problems = fields.Char(tracking=True)
	exercise_ids = fields.One2many('exercise.exercise','form_id')
	exercise_motivated = fields.Selection([
		('yes', 'Yes'),('little', 'A Little'),
		('no', 'No')],tracking=True)
	exercise_problems = fields.Text(tracking=True)
	blood_type = fields.Boolean(default=False)
	vegetarian = fields.Boolean(default=False)
	vegan = fields.Boolean(default=False)
	low_sodium = fields.Boolean(default=False)
	no_dairy = fields.Boolean(default=False)
	no_gluten = fields.Boolean(default=False)
	low_fat = fields.Boolean(default=False)
	high_protein = fields.Boolean(default=False)
	low_carb = fields.Boolean(default=False)
	keto = fields.Boolean(default=False)
	other = fields.Boolean(default=False)
	other_nutrition = fields.Char(tracking=True)
	certain_foods = fields.Char(tracking=True)
	three_meal = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)
	skipping_meal = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)
	meals_per_week = fields.Selection([
		('0-1', '0-1'),('1-3', '1-3'),('3-5', '3-5'),
		('more_than_5', 'More than 5 meals per week')],tracking=True)
	breakfast = fields.Char(tracking=True)
	lunch = fields.Char(tracking=True)
	dinner = fields.Char(tracking=True)
	snacks = fields.Char(tracking=True)
	fluids = fields.Char(tracking=True)
	coffee = fields.Selection([
		('1', '1'),('2-4', '2-4'),
		('more_than_4', 'More than 4')],tracking=True)
	tea = fields.Selection([
		('1', '1'),('2-4', '2-4'),
		('more_than_4', 'More than 4')],tracking=True)
	sodas = fields.Selection([
		('1', '1'),('2-4', '2-4'),
		('more_than_4', 'More than 4')],tracking=True)
	adverse_reactions = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)
	reactions_explain = fields.Char(tracking=True)
	smoke = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)
	packs_per_day = fields.Char(tracking=True)
	smoke_years = fields.Char(tracking=True)
	smoke_types = fields.Selection([
		('cigarettes', 'Cigarettes'),('vape', 'Vape'),
		('cigar', 'Cigar'),('other', 'Other')],tracking=True)
	other_smoke = fields.Char(tracking=True)
	attempted_to_quit = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)
	attempted_method = fields.Char(tracking=True)
	second_hand_smoke = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)
	fillings = fields.Char(tracking=True)
	caps_crowns = fields.Char(tracking=True)
	problems_chewing = fields.Char(tracking=True)
	gold_fillings = fields.Char(tracking=True)
	root_canals = fields.Char(tracking=True)
	tooth_sensitivity = fields.Char(tracking=True)
	implants = fields.Char(tracking=True)
	bleeding_gums = fields.Char(tracking=True)
	gingivitis = fields.Char(tracking=True)
	abscesses = fields.Char(tracking=True)
	other_dental_concerns = fields.Char(tracking=True)
	fillings_removed = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)
	how_removed = fields.Char(tracking=True)
	fillings_removed_ids = fields.One2many('medical.medical','form_id',
				tracking=True,
						domain=[('is_fillings_removed','=',True)])
	born = fields.Selection([
		('term', 'Term'),
		('premature', 'Premature')],tracking=True)
	pregnancy_complications = fields.Selection([
		('yes', 'Yes'),
		('no', 'No')],tracking=True)	
	complications = fields.Char(tracking=True)
	breast = fields.Selection([
		('breast_fed', 'Breast-fed'),
		('bottle_fed', 'Bottle-fed'),('dont_know','Don’t know')],tracking=True)
	breast_fed = fields.Char(tracking=True)
	type_of_bottle_fed = fields.Char(tracking=True)
	solid_food_age = fields.Char(tracking=True)
	wheat_age = fields.Char(tracking=True)
	dairy_age = fields.Char(tracking=True)
	food_symptoms = fields.Selection([
		('yes', 'Yes'),('no', 'No'),
		('dont_know', 'Don’t know')],tracking=True)
	family_disease = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_disease','=',True)])
	inflammatory_immune = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_immune','=',True)])
	respiratory = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_respiratory','=',True)])
	skin_problems = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_skin_problem','=',True)])
	gastrointestinal = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_gastrointestinal','=',True)])
	endocrine_metabolic = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_endocrine_metabolic','=',True)])
	emotional = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_emotional','=',True)])
	urinary = fields.One2many('family.disease','form_id',tracking=True,
					domain=[('is_urinary','=',True)])


	@api.model
	def create(self, vals):
		res = super(IntakeForm, self).create(vals)
		res.get_lines()
		return res

	def get_lines(self):
		self.family_disease = False
		family_disease = []
		obj = self.env['disease.disease'].search([])
		if not self.family_disease:
			for disease in obj:
				family_disease.append((0, 0, {
					'disease_id': disease.id,
					'is_disease':True,
				}))
			self.update({'family_disease': family_disease})
		#######################################################
		self.inflammatory_immune = False
		inflammatory_immune = []
		obj_2 = self.env['immune.symptomology'].search([])
		if not self.inflammatory_immune:
			for symptomology in obj_2:
				inflammatory_immune.append((0, 0, {
					'immune_id': symptomology.id,
					'is_immune':True,
				}))
			self.update({'inflammatory_immune': inflammatory_immune})
		#######################################################
		self.respiratory = False
		respiratory = []
		obj_3 = self.env['respiratory.symptomology'].search([])
		if not self.respiratory:
			for symptomology in obj_3:
				respiratory.append((0, 0, {
					'respiratory_id': symptomology.id,
					'is_respiratory':True,
				}))
			self.update({'respiratory': respiratory})
		#######################################################
		self.skin_problems = False
		skin_problems = []
		obj_4 = self.env['skin_problem.symptomology'].search([])
		if not self.skin_problems:
			for symptomology in obj_4:
				skin_problems.append((0, 0, {
					'skin_problem_id': symptomology.id,
					'is_skin_problem':True,
				}))
			self.update({'skin_problems': skin_problems})
		#######################################################
		self.gastrointestinal = False
		gastrointestinal = []
		obj_5 = self.env['gastrointestinal.symptomology'].search([])
		if not self.gastrointestinal:
			for symptomology in obj_5:
				gastrointestinal.append((0, 0, {
					'gastrointestinal_id': symptomology.id,
					'is_gastrointestinal':True,
				}))
			self.update({'gastrointestinal': gastrointestinal})
		#######################################################
		self.endocrine_metabolic = False
		endocrine_metabolic = []
		obj_6 = self.env['endocrine_metabolic.symptomology'].search([])
		if not self.endocrine_metabolic:
			for symptomology in obj_6:
				endocrine_metabolic.append((0, 0, {
					'endocrine_metabolic_id': symptomology.id,
					'is_endocrine_metabolic':True,
				}))
			self.update({'endocrine_metabolic': endocrine_metabolic})
		#######################################################
		self.emotional = False
		emotional = []
		obj_7 = self.env['emotional.symptomology'].search([])
		if not self.emotional:
			for symptomology in obj_7:
				emotional.append((0, 0, {
					'emotional_id': symptomology.id,
					'is_emotional':True,
				}))
			self.update({'emotional': emotional})
		#######################################################
		self.urinary = False
		urinary = []
		obj_8 = self.env['urinary.symptomology'].search([])
		if not self.urinary:
			for symptomology in obj_8:
				urinary.append((0, 0, {
					'urinary_id': symptomology.id,
					'is_urinary':True,
				}))
			self.update({'urinary': urinary})

class MedicalRecord(models.Model):
	_name = 'medical.medical'

	problem = fields.Text(tracking=True)
	severity = fields.Char(tracking=True)
	prior_treatment = fields.Char(tracking=True)
	success = fields.Char(tracking=True)
	is_health_concerns = fields.Boolean(default=False)
	is_medical_history = fields.Boolean(default=False)
	form_id = fields.Many2one('intake.form')
	medication_food = fields.Char(tracking=True)
	reaction = fields.Char(tracking=True)
	is_allergies = fields.Boolean(default=False)
	date = fields.Date(tracking=True)
	removed_reason = fields.Char(tracking=True,string="Reason")
	is_fillings_removed = fields.Boolean(default=False)



class Exercise(models.Model):
	_name = 'exercise.exercise'

	activity = fields.Char(tracking=True)
	type = fields.Char(tracking=True)
	week_times = fields.Char(string="# of times per week",tracking=True)
	duration = fields.Char(string="Duration (minutes)",tracking=True)
	form_id = fields.Many2one('intake.form')



class FamilyDisease(models.Model):
	_name = 'family.disease'

	disease_id = fields.Many2one('disease.disease',tracking=True)
	m_grand_mother = fields.Boolean(default=False,tracking=True)
	m_grand_father = fields.Boolean(default=False,tracking=True)
	p_grand_mother = fields.Boolean(default=False,tracking=True)
	p_grand_father = fields.Boolean(default=False,tracking=True)
	mother = fields.Boolean(default=False,tracking=True)
	father = fields.Boolean(default=False,tracking=True)
	brother = fields.Boolean(default=False,tracking=True)
	sister = fields.Boolean(default=False,tracking=True)
	child = fields.Boolean(default=False,tracking=True)
	other = fields.Boolean(default=False,tracking=True)
	form_id = fields.Many2one('intake.form')
	immune_id = fields.Many2one('immune.symptomology',tracking=True)
	respiratory_id = fields.Many2one('respiratory.symptomology',tracking=True)
	skin_problem_id = fields.Many2one('skin_problem.symptomology',tracking=True)
	gastrointestinal_id = fields.Many2one('gastrointestinal.symptomology',tracking=True)
	endocrine_metabolic_id = fields.Many2one('endocrine_metabolic.symptomology',tracking=True)
	emotional_id = fields.Many2one('emotional.symptomology',tracking=True)
	urinary_id = fields.Many2one('urinary.symptomology',tracking=True)
	mild = fields.Boolean(default=False,tracking=True)
	moderate = fields.Boolean(default=False,tracking=True)
	severe = fields.Boolean(default=False,tracking=True)
	is_disease = fields.Boolean(default=False)
	is_immune = fields.Boolean(default=False)
	is_respiratory = fields.Boolean(default=False)	
	is_skin_problem = fields.Boolean(default=False)	
	is_gastrointestinal = fields.Boolean(default=False)	
	is_endocrine_metabolic = fields.Boolean(default=False)	
	is_emotional = fields.Boolean(default=False)	
	is_urinary = fields.Boolean(default=False)	



class Disease(models.Model):
	_name = 'disease.disease'

	name = fields.Char(tracking=True)

class Immune(models.Model):
	_name = 'immune.symptomology'

	name = fields.Char(tracking=True)

class Respiratory(models.Model):
	_name = 'respiratory.symptomology'

	name = fields.Char(tracking=True)

class SkinProblem(models.Model):
	_name = 'skin_problem.symptomology'

	name = fields.Char(tracking=True)

class Gastrointestinal(models.Model):
	_name = 'gastrointestinal.symptomology'

	name = fields.Char(tracking=True)

class EndocrineMetabolic(models.Model):
	_name = 'endocrine_metabolic.symptomology'

	name = fields.Char(tracking=True)

class Emotional(models.Model):
	_name = 'emotional.symptomology'

	name = fields.Char(tracking=True)

class Urinary(models.Model):
	_name = 'urinary.symptomology'

	name = fields.Char(tracking=True)