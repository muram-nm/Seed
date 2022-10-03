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
    portal_user = fields.Many2one('res.users',string="Portal User",domain=lambda self: [('groups_id', 'in', self.env.ref('base.group_portal').id)])

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
        
        # write in related partner
        result.partner_id.write({
            'qid':result.qid,
            'gender':result.gender,
            'date_of_birth':result.date_of_birth,
            'qr_code':result.qr_code,
        })
        # give portal access to the customer
        for customer in result:           
            # protal_wizard = customer.partner_id.env['portal.wizard'].create({})
            # protal_wizard_user = self.env['portal.wizard.user'].create({
            #     'partner_id':customer.partner_id.id,
            #     'email':customer.email,
            #     'wizard_id':protal_wizard.id
            #     })

            # protal_wizard_user.action_grant_access()
            print('customer',customer.partner_id)
            customer.action_grant_access()
        return result
    def action_grant_access(self):
        """Grant the portal access to the partner.

        If the partner has no linked user, we will create a new one in the same company
        as the partner (or in the current company if not set).

        An invitation email will be sent to the partner.
        """
        self.ensure_one()
        self._assert_user_email_uniqueness()


        group_portal = self.env.ref('base.group_portal')
        # group_public = self.env.ref('base.group_public')

        # update partner email, if a new one was introduced
        if self.partner_id.email != self.email:
            self.partner_id.write({'email': self.email})

        user_sudo = self.user_id.sudo()

        if not user_sudo:
            # create a user if necessary and make sure it is in the portal group
            company = self.partner_id.company_id or self.env.company
            user_sudo = self.sudo().with_company(company.id)._create_user()

        if not user_sudo.active:
            user_sudo.write({'active': True, 'groups_id': [(4, group_portal.id)]})
            # prepare for the signup process
            user_sudo.partner_id.signup_prepare()
        self.portal_user = user_sudo.id
        self._send_email()

        return True
    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': email_normalize(self.email),
            'login': email_normalize(self.email),
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })

    def _send_email(self):
        """ send notification email to a new portal user """
        self.ensure_one()

        # determine subject and body in the portal user's language
        template = self.env.ref('nm_health_wellness_reception_sales.mail_template_data_portal_welcome')
        if not template:
            raise UserError(_('The template "Portal: new user" not found for sending email to the portal user.'))

        lang = self.user_id.sudo().lang
        partner = self.partner_id
        print('customersssssssssss',partner)
        portal_url = partner.with_context(signup_force_type_in_url='', lang=lang)._get_signup_url_for_action()[partner.id]
        # partner.signup_prepare()

        template.with_context(dbname=self._cr.dbname, portal_url=portal_url, lang=lang).send_mail(self.id, force_send=True)

        return True
    def action_show_orders(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': self.name + "' Orders",
            'res_model': 'reception.order',
            'view_mode': 'list,calendar,kanban,form',
            'search_view_id': self.env.ref('nm_health_wellness_reception_sales.reception_order_search_view').id,
            'domain': [("partner_id", "=", self.partner_id.id)],
        }
    def _assert_user_email_uniqueness(self):
        """Check that the email can be used to create a new user."""
        self.ensure_one()

        email = email_normalize(self.email)

        if not email:
            raise UserError(_('The contact "%s" does not have a valid email.', self.partner_id.name))

        user = self.env['res.users'].sudo().with_context(active_test=False).search([
            ('id', '!=', self.user_id.id),
            ('login', '=ilike', email),
        ])

        if user:
            raise UserError(_('The contact "%s" has the same email has an existing user (%s).', self.partner_id.name, user.name))



class ResPartner(models.Model):
    _inherit = 'res.partner'

    qid = fields.Char('QID')
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female')])
    date_of_birth = fields.Date('Date of Birth')
    qr_code = fields.Char(string="QR Code")

    def write(self, vals):
        customer_id = self.env['reception.customer'].search([('partner_id', '=', self.id)], limit=1)
        if customer_id and 'name' in vals.keys():
            raise UserError(_("QID and Name can not be changed once the customer is created."))
        return super(ResPartner, self).write(vals)
