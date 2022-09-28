# -*- coding: utf-8 -*-

import base64
from odoo.tools.image import image_data_uri
import werkzeug
import werkzeug.exceptions
from odoo import api, models, fields, _
from odoo.exceptions import UserError, ValidationError, RedirectWarning
from odoo.tools import email_normalize


class ReceptionCustomer(models.Model):
    _name = 'reception.customer'
    _description = 'Reception Customer'
    _inherits = {'res.partner': 'partner_id'}
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _sql_constraints = [('unique_qid', 'UNIQUE(qid)', 'QID must be unique')]

    partner_id = fields.Many2one('res.partner', string='Related Partner', required=True, ondelete='cascade',
                                 tracking=True)
    customer_no = fields.Char('Customer No.', required=True, copy=False, readonly=True, index=True, tracking=True,
                              default=lambda self: _('New'))
    qid = fields.Char('QID', required=True, tracking=True)
    mobile = fields.Char(tracking=True)
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female')], tracking=True,default="male")
    date_of_birth = fields.Date('Date of Birth', required=True, tracking=True)
    age = fields.Integer(compute='_compute_age', tracking=True)
    qr_code = fields.Char(string="QR Code",
                          compute="_compute_qr_code", store=True)
    orders = fields.Integer(compute='_compute_orders')
    last_order_date = fields.Date(compute='_compute_last_order_date')
    

    @api.constrains('qid')
    def check_qid(self):
        if self.qid:
            if not self.qid.isnumeric() or len(self.qid) != 11:
                raise ValidationError(_('QID It must consist of 11 numbers (letters or signs are not allowed)'))

    @api.depends("partner_id")
    def _compute_orders(self):
        for customer in self:
            reception_order_ids = self.env['reception.order'].search([('partner_id', '=', customer.partner_id.id)])
            customer.orders = len(reception_order_ids)

    @api.depends("partner_id")
    def _compute_last_order_date(self):
        for customer in self:
            reception_order_id = self.env['reception.order'].search([('partner_id', '=', customer.partner_id.id)], limit=1, order="create_date desc")
            customer.last_order_date = reception_order_id.create_date

    def get_qr_vals(self):
        return "Customer Info:\n NAME: %s\n CUSTOMER NO: %s\n QID: %s\n GENDER: %s\n DATE OF BIRTH: %s\n" % (
                self.name, self.customer_no, self.qid, self.gender, self.date_of_birth)

    @api.depends("name", "customer_no", "qid", "gender", "date_of_birth")
    def _compute_qr_code(self):
        for customer in self:
            vals = customer.get_qr_vals()
            try:
                barcode = self.env['ir.actions.report'].barcode('QR', vals, width=100, height=100)
            except (ValueError, AttributeError):
                raise werkzeug.exceptions.HTTPException(description='Cannot convert into barcode.')
            qr_code = image_data_uri(base64.b64encode(barcode))
            if qr_code:
                customer.qr_code = '<img class="border border-dark rounded" src="{qr_code}"/>'.format(qr_code=qr_code)
            else:
                customer.qr_code = False

    @api.depends('date_of_birth')
    def _compute_age(self):
        today = fields.Date.today()
        for customer in self:
            customer.age = customer.date_of_birth and int((today - customer.date_of_birth).days / 365.2425)

    def write(self, vals):
        if self.customer_no != _('New') and ('name' in list(vals.keys()) or 'qid' in list(vals.keys())):
            raise UserError(_("QID and Name can not be changed once the customer is created."))
        return super(ReceptionCustomer, self).write(vals)

    @api.model
    def create(self, vals):
        if vals.get('customer_no', _('New')) == _('New'):
            vals['customer_no'] = self.env['ir.sequence'].next_by_code('reception.customer') or _('New')
        result = super(ReceptionCustomer, self).create(vals)

        # give portal access to the customer
        group_portal = self.env.ref('base.group_portal')
        group_public = self.env.ref('base.group_public')
        for customer in result:
            user_sudo = customer.partner_id.user_id.sudo()
            if not user_sudo:
                # create a user if necessary and make sure it is in the portal group
                company = customer.partner_id.company_id or self.env.company
                user_sudo = self.sudo().with_company(company.id)._create_user(customer)
            if not user_sudo.active:
                user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id), (3, group_public.id)]})
                # prepare for the signup process
                user_sudo.partner_id.signup_prepare()
                self.with_context(active_test=True)._send_email(customer)
        return result

    def _create_user(self,customer):
        """ create a new user for
            :returns record of res.users
        """
        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': email_normalize(customer.email),
            'login': email_normalize(customer.email),
            'partner_id': customer.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })

    def _send_email(self,customer):
        """ send notification email to a new portal user """
        self.ensure_one()

        # determine subject and body in the portal user's language
        template = self.env.ref('portal.mail_template_data_portal_welcome')
        if not template:
            raise UserError(_('The template "Portal: new user" not found for sending email to the portal user.'))

        lang = customer.partner_id.user_id.sudo().lang
        partner = customer.partner_id.user_id.sudo().partner_id

        portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
        partner.signup_prepare()

        template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(self.id, force_send=True)

        return True


    def action_show_orders(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id("nm_health_wellness_reception_sales.action_reception_order")
        action['name'] = self.name + "' Orders"
        action['domain'] = [("partner_id", "=", self.partner_id.id)]
        return action



class ResPartner(models.Model):
    _inherit = 'res.partner'

    def write(self, vals):
        customer_id = self.env['reception.customer'].search([('partner_id', '=', self.id)], limit=1)
        if customer_id and 'name' in vals.keys():
            raise UserError(_("QID and Name can not be changed once the customer is created."))
        return super(ResPartner, self).write(vals)
