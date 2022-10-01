# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, tools


class ReportUnitGuestUser(models.Model):
    _name = "report.unit.guest.user"
    _description = "Guest Analysis"
    _order = 'name desc, unit_id'
    _auto = False

    name = fields.Char(string='Guest', readonly=True)
    user_ids = fields.Many2many('res.users', relation='unit_guest_user_rel', column1='guest_id', column2='user_id',
                                string='Assignees', readonly=True)
    create_date = fields.Datetime("Create Date", readonly=True)
    date_assign = fields.Datetime(string='Assignment Date', readonly=True)
    date_end = fields.Datetime(string='Ending Date', readonly=True)
    date_last_stage_update = fields.Datetime(string='Last Stage Update', readonly=True)
    unit_id = fields.Many2one('unit.unit', string='Unite', readonly=True)
    working_days_close = fields.Float(string='Working Days to Close',
        digits=(16,2), readonly=True, group_operator="avg",
        help="Number of Working Days to close the task")
    working_days_open = fields.Float(string='Working Days to Assign',
        digits=(16,2), readonly=True, group_operator="avg",
        help="Number of Working Days to open the task")
    delay_endings_days = fields.Float(string='Days to Deadline', digits=(16, 2), group_operator="avg", readonly=True)
    nbr = fields.Integer('# of Tasks', readonly=True)  # TDE FIXME master: rename into nbr_tasks
    working_hours_open = fields.Float(string='Working Hours to Assign', digits=(16, 2), readonly=True, group_operator="avg", help="Number of Working Hours to open the task")
    working_hours_close = fields.Float(string='Working Hours to Close', digits=(16, 2), readonly=True, group_operator="avg", help="Number of Working Hours to close the task")
    rating_last_value = fields.Float('Rating Value (/5)', group_operator="avg", readonly=True, groups="project.group_project_rating")
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High')
        ], readonly=True, string="Priority")
    state = fields.Selection([
            ('normal', 'In Progress'),
            ('blocked', 'Blocked'),
            ('done', 'Ready for Next Stage')
        ], string='Kanban State', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True)
    partner_id = fields.Many2one('reception.customer', string='Customer', readonly=True)
    stage_id = fields.Many2one('unit.guest.stages', string='Stage', readonly=True)
    guest_id = fields.Many2one('unit.guest', string='Guest', readonly=True)

    def _select(self):
        select_str = """
             SELECT
                    (select 1 ) AS nbr,
                    t.id as id,
                    t.id as guest_id,
                    t.create_date as create_date,
                    t.date_assign as date_assign,
                    t.date_end as date_end,
                    t.date_last_stage_update as date_last_stage_update,
                    t.unit_id,
                    t.priority,
                    t.partner_id,
                    t.stage_id as stage_id,
                    t.kanban_state as state,
                  
                    (extract('epoch' from (t.date_end-(now() at time zone 'UTC'))))/(3600*24)  as delay_endings_days
        """
        return select_str

    def _group_by(self):
        group_by_str = """
                GROUP BY
                    t.id,
                    t.create_date,
                    t.write_date,
                    t.date_assign,
                    t.date_end,
                    t.date_last_stage_update,
                    t.unit_id,
                    t.priority,
                    t.company_id,
                    t.stage_id
        """
        return group_by_str

    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
            CREATE view %s as
              %s
              FROM unit_guest t
              LEFT JOIN unit_unit tu on tu.id=t.unit_id
                WHERE t.active = 'true'
                AND t.unit_id IS NOT NULL
                %s
        """ % (self._table, self._select(), self._group_by()))
