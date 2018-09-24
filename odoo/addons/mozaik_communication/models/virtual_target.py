# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualTarget(models.Model):
    _name = "virtual.target"
    _description = "Searching Result"
    _auto = False
    # Todo; tocheck: this model shouldn't inherit from abstract virtual model
    # because it doesn't have same fields
    _inherit = [
        'abstract.virtual.model',
        'abstract.term.finder'
    ]

    membership_state_id = fields.Many2one(
        comodel_name='membership.state', string='Membership State')
    display_name = fields.Char()
    technical_name = fields.Char()
    lastname = fields.Char()
    firstname = fields.Char()
    email = fields.Char(string='Email Coordinate')
    postal = fields.Char(string='Postal Coordinate')
    email_failure_counter = fields.Integer(string='Email Bounce Counter')
    postal_failure_counter = fields.Integer(string='Postal Bounce Counter')
    zip = fields.Char("Zip Code")
    country_id = fields.Many2one(
        comodel_name='res.country', string='Country')

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = super()._get_select() + """,
            pc.is_main AS main_postal,
            pc.failure_counter as postal_failure_counter,
            CASE
                WHEN pc.vip is TRUE
                THEN 'VIP'
                ELSE adr.name
            END as postal,
            adr.zip as zip,
            adr.country_id as country_id,
            e.is_main AS main_email,
            e.failure_counter as email_failure_counter,
            CASE
                WHEN e.vip is TRUE
                THEN 'VIP'
                ELSE e.email
            END as email,
            p.membership_state_id AS membership_state_id,
            p.display_name AS display_name,
            p.technical_name AS technical_name,
            p.lastname AS lastname,
            p.firstname AS firstname"""
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        return """
            FROM res_partner p

            LEFT OUTER JOIN email_coordinate e
            ON (e.partner_id = p.id
            AND e.active IS TRUE)

            LEFT OUTER JOIN postal_coordinate pc
            ON (pc.partner_id = p.id
            AND pc.active IS TRUE)

            LEFT OUTER JOIN address_address adr
            ON (adr.id = pc.address_id)"""

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active IS TRUE"
