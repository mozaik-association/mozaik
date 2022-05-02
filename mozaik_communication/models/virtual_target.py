# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualTarget(models.Model):
    _name = "virtual.target"
    _description = "Searching Result"
    _inherit = [
        "abstract.virtual.model",
    ]
    _auto = False

    result_id = fields.Many2one(store=False)
    membership_state_id = fields.Many2one(
        comodel_name="membership.state", string="Membership State"
    )
    display_name = fields.Char()
    technical_name = fields.Char()
    lastname = fields.Char()
    firstname = fields.Char()
    email = fields.Char(string="Email Coordinate")
    postal = fields.Char(string="Postal Coordinate")
    zip = fields.Char("Zip Code")
    country_id = fields.Many2one(comodel_name="res.country", string="Country")
    email_bounce_counter = fields.Integer()
    last_postal_failure_date = fields.Datetime()
    postal_bounced = fields.Boolean()

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = (
            super()._get_select()
            + """,
            adr.name as postal,
            adr.zip as zip,
            adr.country_id as country_id,
            p.last_postal_failure_date,
            p.postal_bounced,
            p.email as email,
            p.membership_state_id AS membership_state_id,
            p.display_name AS display_name,
            p.technical_name AS technical_name,
            p.lastname AS lastname,
            p.firstname AS firstname,
            p.email_bounced AS email_bounce_counter"""
        )
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        return """
            FROM res_partner p

            LEFT OUTER JOIN address_address adr
            ON (adr.id = p.address_address_id)"""

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active IS TRUE"

    @api.model
    def _select_virtual_target(self):
        return ""

    @api.model
    def _from_virtual_target(self):
        return ""
