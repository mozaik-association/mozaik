# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerInstance(models.Model):
    _name = "virtual.partner.instance"
    _description = "Partner/Instance"
    _inherit = [
        "abstract.virtual.model",
    ]
    _auto = False

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
        comodel_name="res.country",
        string="Nationality",
    )
    membership_state_id = fields.Many2one(
        comodel_name="membership.state",
        string="State",
    )
    email = fields.Char(string="Email")
    address_address_id = fields.Many2one(
        comodel_name="address.address", string="Address"
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
            p.local_voluntary,
            p.regional_voluntary,
            p.national_voluntary,
            p.local_only,
            p.is_donor,
            p.is_volunteer,
            p.nationality_id,
            p.membership_state_id,
            p.email,
            p.address_address_id"""
        )
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        from_query = """FROM res_partner AS p"""
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active = TRUE AND p.identifier > 0"
