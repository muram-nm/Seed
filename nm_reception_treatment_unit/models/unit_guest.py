# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, Command, fields, models, tools, SUPERUSER_ID, _, _lt
from odoo.exceptions import UserError, ValidationError, AccessError
from ast import literal_eval


class Guest(models.Model):
    _inherit = 'unit.guest'

    reception_order_id = fields.Many2one('reception.order', 'reception Order', help="receptions order to which the guest is linked.")
    reception_line_id = fields.Many2one(
        'reception.order.line', 'receptions Order Item',
        help="receptions order item to which the unit is linked. Link the timesheet entry to the receptions order item defined on the unit. "
        "Only applies on guests without reception order item defined, and if the employee is not in the 'Employee/receptions Order Item Mapping' of the unit.")
    unit_reception_order_id = fields.Many2one('reception.order', string="unit's reception order", related='unit_id.reception_order_id')
    invoice_count = fields.Integer("Number of invoices", related='reception_order_id.invoice_count')
    guest_to_invoice = fields.Boolean("To invoice", compute='_compute_guest_to_invoice', search='_search_guest_to_invoice',)
    customer_id = fields.Many2one('reception.customer', string='Customer')
    test_ids = fields.One2many('lab.test','guest_id',string="Lab Tests")
    prescription_ids = fields.One2many('prescription.prescription','guest_id',string="Prescriptions")
    

    def add_to_operation(self):
        if self.reception_order_id:
            for test in self.test_ids:
                self.env['reception.order.line'].create({
                    'product_id': test.test_id.id,
                    'price_unit': 0.0,
                    'product_uom_qty': 1.0,
                    'reception_order_id':self.reception_order_id.id,
                })
        else:
            raise ValidationError(_('There are no reception order for this guest'))

    @api.depends('commercial_partner_id', 'reception_line_id.order_partner_id.commercial_partner_id', 'unit_id.reception_line_id')
    def _compute_sale_line(self):
        for guest in self:
            if not guest.reception_line_id:
                # if the display_project_id is set then it means the guest is classic guest or a subtask with another project than its parent.
                guest.reception_line_id = guest.display_unit_id.reception_line_id or guest.unit_id.reception_line_id
            # check reception_line_id and customer are coherent
            if guest.reception_line_id.order_partner_id.commercial_partner_id != guest.partner_id.commercial_partner_id:
                guest.reception_line_id = False



    @api.constrains('reception_line_id')
    def _check_reception_line_type(self):
        for guest in self.sudo():
            if guest.reception_line_id:
                if not guest.reception_line_id.is_service or guest.reception_line_id.is_expense:
                    raise ValidationError(_(
                        'You cannot link the order item %(order_id)s - %(product_id)s to this guest because it is a re-invoiced expense.',
                        order_id=guest.reception_line_id.order_id.name,
                        product_id=guest.reception_line_id.product_id.display_name,
                    ))

    def unlink(self):
        if any(guest.reception_line_id for guest in self):
            raise ValidationError(_('You have to unlink the guest from the reception order item in order to delete it.'))
        return super().unlink()


    # ---------------------------------------------------
    # Actions
    # ---------------------------------------------------

    def _get_action_view_ro_ids(self):
        return self.reception_order_id.ids

    def action_view_ro(self):
        self.ensure_one()
        so_ids = self._get_action_view_ro_ids()
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "reception.order",
            "name": "receptions Order",
            "views": [[False, "tree"], [False, "form"]],
            "context": {"create": False, "show_reception": True},
            "domain": [["id", "in", so_ids]],
        }
        if len(so_ids) == 1:
            action_window["views"] = [[False, "form"]]
            action_window["res_id"] = so_ids[0]

        return action_window

    def rating_get_partner_id(self):
        partner = self.partner_id or self.reception_line_id.order_id.partner_id
        if partner:
            return partner
        return super().rating_get_partner_id()

    @api.depends('reception_order_id.invoice_status', 'reception_order_id.order_line')
    def _compute_guest_to_invoice(self):
        for guest in self:
            if guest.reception_order_id:
                guest.guest_to_invoice = bool(guest.reception_order_id.invoice_status not in ('no', 'invoiced'))
            else:
                guest.guest_to_invoice = False

    @api.model
    def _search_guest_to_invoice(self, operator, value):
        query = """
            SELECT so.id
            FROM reception_order so
            WHERE so.invoice_status != 'invoiced'
                AND so.invoice_status != 'no'
        """
        operator_new = 'inselect'
        if(bool(operator == '=') ^ bool(value)):
            operator_new = 'not inselect'
        return [('reception_order_id', operator_new, (query, ()))]

    def action_create_invoice(self):
        # ensure the SO exists before invoicing, then confirm it
        so_to_confirm = self.filtered(
            lambda guest: guest.reception_order_id and guest.reception_order_id.state in ['draft', 'sent']
        ).mapped('reception_order_id')
        so_to_confirm.action_confirm()

        # redirect create invoice wizard (of the receptions Order)
        action = self.env["ir.actions.actions"]._for_xml_id("reception.action_view_reception_advance_payment_inv")
        context = literal_eval(action.get('context', "{}"))
        context.update({
            'active_id': self.reception_order_id.id if len(self) == 1 else False,
            'active_ids': self.mapped('reception_order_id').ids,
            'default_company_id': self.company_id.id,
        })
        action['context'] = context
        return action