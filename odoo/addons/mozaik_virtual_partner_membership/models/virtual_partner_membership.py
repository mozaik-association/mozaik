# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerMembership(models.Model):
    _name = "virtual.partner.membership"
    _description = "Partner/Membership"
    _inherit = "abstract.virtual.target"
    _auto = False
    _terms = [
        'competency_ids',
        'interest_ids',
    ]

    partner_id = fields.Many2one(
        domain=[('is_company', '=', False), ('identifier', '>', 0)],
    )
    membership_state_id = fields.Many2one(
        comodel_name='membership.state',
        string="State",
    )
    del_doc_date = fields.Date(
        string='Welcome Documents Sent Date',
    )
    del_mem_card_date = fields.Date(
        string="Member Card Sent Date",
    )
    reference = fields.Char()
    is_donor = fields.Boolean(
        string="Is a donor",
    )
    is_volunteer = fields.Boolean(
        string="Is a volunteer",
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = """SELECT
                p.id as id,
                concat(p.id, '/', pc.id, '/', e.id) as common_id,
                p.id as partner_id,
                p.int_instance_id as int_instance_id,
                p.del_doc_date as del_doc_date,
                p.del_mem_card_date as del_mem_card_date,
                p.reference as reference,
                e.id as email_coordinate_id,
                pc.id as postal_coordinate_id,
                p.identifier as identifier,
                p.birth_date as birth_date,
                p.gender as gender,
                p.lang as lang,
                p.employee as employee,
                pc.unauthorized as postal_unauthorized,
                pc.vip as postal_vip,
                e.vip as email_vip,
                e.unauthorized as email_unauthorized,
                p.membership_state_id as membership_state_id,
                CASE
                    WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                    THEN True
                    ELSE False
                END AS active,
                p.is_donor,
                p.is_volunteer"""
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        from_query = """FROM res_partner AS p
            JOIN membership_line AS m
                ON (m.partner_id = p.id
                AND m.active = TRUE)
            LEFT OUTER JOIN postal_coordinate AS pc
                ON (pc.partner_id = p.id
                AND pc.active = TRUE
                AND pc.is_main = TRUE)
            LEFT OUTER JOIN email_coordinate AS e
                ON (e.partner_id = p.id
                AND e.active = TRUE
                AND e.is_main = TRUE)"""
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active = TRUE"
