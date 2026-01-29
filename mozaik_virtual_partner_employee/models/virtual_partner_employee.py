# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerEmployee(models.Model):
    _name = "virtual.partner.employee"
    _description = "Partner/Employee"
    _inherit = ["abstract.virtual.model"]
    _auto = False

    employee_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Employee",
    )
    department_id = fields.Many2one(
        comodel_name="hr.department",
        string="Department",
    )
    parent_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Manager",
    )
    coach_id = fields.Many2one(
        comodel_name="hr.employee",
        string="Coach",
    )
    job_id = fields.Many2one(
        comodel_name="hr.job",
        string="Job Position",
    )
    work_email = fields.Char(
        string="Work Email",
    )
    work_phone = fields.Char(
        string="Work Phone",
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = (
            super()._get_select()
            + """,
            e.id as employee_id,
            e.department_id,
            e.parent_id,
            e.coach_id,
            e.job_id,
            e.work_email,
            e.work_phone"""
        )
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        from_query = """FROM hr_employee AS e
            JOIN res_partner AS p
                ON p.id = e.address_home_id
                """
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active = TRUE AND e.active = TRUE"

    @api.model
    def _get_order_by(self):
        return "%s, %s" % (super()._get_order_by(), "employee_id")
