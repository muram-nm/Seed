# -*- coding:utf-8 -*-

from ast import literal_eval

from odoo import api, fields, models, _, _lt
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from odoo.osv.query import Query



class Unit(models.Model):
    _inherit = 'unit.unit'

    reception_order_id = fields.Many2one('reception.order',string='Reception Order')

    

    reception_line_id = fields.Many2one(
        'reception.order.line', 'Reception Order Item', copy=False,
        domain="[('is_service', '=', True), ('is_expense', '=', False), ('order_id', '=', reception_order_id), ('state', 'in', ['sale', 'done']), '|', ('company_id', '=', False), ('company_id', '=', company_id)]",
        help="reception order item to which the unit is linked. Link the timesheet entry to the reception order item defined on the unit. "
        "Only applies on guests without reception order item defined, and if the employee is not in the 'Employee/Reception Order Item Mapping' of the unit.")
    reception_order_id = fields.Many2one('reception.order', 'reception Order',
        domain="[('order_line.product_id.type', '=', 'service'), ('partner_id', '=', partner_id), ('state', 'in', ['sale', 'done'])]",
        copy=False, help="reception order to which the unit is linked.")

    _sql_constraints = [
        ('reception_order_required_if_reception_line', "CHECK((reception_line_id IS NOT NULL AND reception_order_id IS NOT NULL) OR (reception_line_id IS NULL))", 'The unit should be linked to a reception order to select a reception order item.'),
    ]


    @api.model
    def _map_guests_default_valeus(self, guest, unit):
        defaults = super()._map_guests_default_valeus(guest, unit)
        defaults['reception_line_id'] = False
        return defaults

    def action_view_ro(self):
        self.ensure_one()
        action_window = {
            "type": "ir.actions.act_window",
            "res_model": "reception.order",
            "name": "Reception Order",
            "views": [[False, "form"]],
            "context": {"create": False, "show_reception": True},
            "res_id": self.reception_order_id.id
        }
        return action_window


    def action_create_invoice(self):
        if not self.has_any_so_to_invoice:
            raise UserError(_("There is nothing to invoice in this unit."))
        action = self.env["ir.actions.actions"]._for_xml_id("sale.action_view_sale_advance_payment_inv")
        so_ids = (self.reception_order_id | self.guest_ids.reception_order_id).filtered(lambda so: so.invoice_status == 'to invoice').ids
        action['context'] = {
            'active_id': so_ids[0] if len(so_ids) == 1 else False,
            'active_ids': so_ids
        }
        return action

    # ----------------------------
    #  unit Updates
    # ----------------------------

    def _get_reception_order_stat_button(self):
        self.ensure_one()
        return {
            'icon': 'dollar',
            'text': _lt('Unit Order'),
            'action_type': 'object',
            'action': 'action_view_ro',
            'show': bool(self.reception_order_id),
            'sequence': 1,
        }

    def _fetch_reception_order_items(self, domain_per_model=None, limit=None, offset=None):
        return self.env['sale.order.line'].browse(self._fetch_reception_order_item_ids(domain_per_model, limit, offset))

    def _fetch_reception_order_item_ids(self, domain_per_model=None, limit=None, offset=None):
        if not self:
            return []
        query = self._get_reception_order_items_query(domain_per_model)
        query.limit = limit
        query.offset = offset
        query_str, params = query.select('DISTINCT reception_line_id')
        self._cr.execute(query_str, params)
        return [row[0] for row in self._cr.fetchall()]

    def _get_reception_orders(self):
        return self._get_reception_order_items().order_id

    def _get_reception_order_items(self):
        return self._fetch_reception_order_items()

    def _get_reception_order_items_query(self, domain_per_model=None):
        if domain_per_model is None:
            domain_per_model = {}
        unit_domain = [('id', 'in', self.ids), ('reception_line_id', '!=', False)]
        if 'unit.unit' in domain_per_model:
            unit_domain = expression.AND([unit_domain, domain_per_model['unit.unit']])
        unit_query = self.env['unit.unit']._where_calc(unit_domain)
        self._apply_ir_rules(unit_query, 'read')
        unit_query_str, unit_params = unit_query.select('id', 'reception_line_id')

        guest = self.env['unit.guest']
        guest_domain = [('unit_id', 'in', self.ids), ('reception_line_id', '!=', False)]
        if guest._name in domain_per_model:
            guest_domain = expression.AND([guest_domain, domain_per_model[guest._name]])
        guest_query = guest._where_calc(guest_domain)
        guest._apply_ir_rules(guest_query, 'read')
        guest_query_str, guest_params = guest_query.select(f'{guest._table}.unit_id AS id', f'{guest._table}.reception_line_id')

        query = Query(self._cr, 'unit_reception_order_item', ' UNION '.join([unit_query_str, guest_query_str]))
        query._where_params = unit_params + guest_params
        return query

  
  