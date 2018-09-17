# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerInstance(models.Model):
    _name = "virtual.partner.instance"
    _description = "Partner/Instance"
    _inherit = "abstract.virtual.target"
    _auto = False
    _terms = ['interest_ids', 'competency_ids']

    partner_id = fields.Many2one(
        domain=[('is_assembly', '=', False)],
    )
    membership_state_id = fields.Many2one(
        comodel_name='membership.state',
        string='State',
    )
    main_postal = fields.Boolean(
        string='Main Address',
    )
    postal_category_id = fields.Many2one(
        comodel_name='coordinate.category',
        string='Postal Coordinate Category',
    )
    email_category_id = fields.Many2one(
        comodel_name='coordinate.category',
        string='Email Coordinate Category',
    )
    main_email = fields.Boolean(
    )
    is_donor = fields.Boolean(
        string="Is a donor",
    )
    is_volunteer = fields.Boolean(
        string="Is a volunteer",
    )
    local_voluntary = fields.Boolean()
    regional_voluntary = fields.Boolean()
    national_voluntary = fields.Boolean()
    local_only = fields.Boolean()
    nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = """SELECT
            CONCAT(p.id, '/', pc.id, '/', e.id) AS common_id,
            p.id AS partner_id,
            p.int_instance_id AS int_instance_id,
            e.id AS email_coordinate_id,
            pc.id AS postal_coordinate_id,
            pc.coordinate_category_id AS postal_category_id,
            p.is_company AS is_company,
            p.identifier AS identifier,
            p.birth_date AS birth_date,
            p.gender AS gender,
            p.lang AS lang,
            p.employee AS employee,
            p.local_voluntary,
            p.regional_voluntary,
            p.national_voluntary,
            p.local_only,
            p.nationality_id,
            pc.unauthorized AS postal_unauthorized,
            pc.vip AS postal_vip,
            pc.is_main AS main_postal,
            e.vip AS email_vip,
            e.coordinate_category_id AS email_category_id,
            e.is_main AS main_email,
            e.unauthorized AS email_unauthorized,
            ms.id AS membership_state_id,
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
            LEFT OUTER JOIN membership_state AS ms
                ON (ms.id = p.membership_state_id)
            LEFT OUTER JOIN postal_coordinate AS pc
                ON (pc.partner_id = p.id
                AND pc.active = TRUE)
            LEFT OUTER JOIN email_coordinate AS e
                ON (e.partner_id = p.id
                AND e.active = TRUE)"""
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active = TRUE AND p.identifier > 0"
