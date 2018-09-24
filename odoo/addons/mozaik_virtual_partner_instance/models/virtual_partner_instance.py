# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerInstance(models.Model):
    _name = "virtual.partner.instance"
    _description = "Partner/Instance"
    _inherit = "abstract.virtual.model"
    _auto = False
    _terms = ['interest_ids', 'competency_ids']

    local_voluntary = fields.Boolean()
    regional_voluntary = fields.Boolean()
    national_voluntary = fields.Boolean()
    local_only = fields.Boolean()
    is_donor = fields.Boolean(
        string="Is a donor",
    )
    is_volunteer = fields.Boolean(
        string="Is a volunteer",
    )
    nationality_id = fields.Many2one(
        comodel_name='res.country',
        string='Nationality',
    )
    postal_category_id = fields.Many2one(
        comodel_name='coordinate.category',
        string='Postal Coordinate Category',
    )
    main_postal = fields.Boolean(
        string='Main Address',
    )
    email_category_id = fields.Many2one(
        comodel_name='coordinate.category',
        string='Email Coordinate Category',
    )
    main_email = fields.Boolean(
    )
    membership_state_id = fields.Many2one(
        comodel_name='membership.state',
        string='State',
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = super()._get_select() + """,
            p.local_voluntary,
            p.regional_voluntary,
            p.national_voluntary,
            p.local_only,
            p.is_donor,
            p.is_volunteer,
            p.nationality_id,
            pc.coordinate_category_id AS postal_category_id,
            pc.is_main AS main_postal,
            e.coordinate_category_id AS email_category_id,
            e.is_main AS main_email,
            ms.id AS membership_state_id"""
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
