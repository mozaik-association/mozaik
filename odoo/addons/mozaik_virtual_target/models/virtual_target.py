# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, models


class VirtualTarget(models.Model):
    _name = "virtual.target"
    _description = "Searching Result"
    _auto = False
    # Todo; tocheck: this model shouldn't inherit from abstract virtual model
    # because it doesn't have same fields
    _inherit = [
        'virtual.master.partner',
        'abstract.virtual.target',
        'abstract.term.finder'
    ]

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = """SELECT
            *,
            CONCAT(
                partner_id,
                '/',
                postal_coordinate_id,
                '/',
                email_coordinate_id
            ) AS id"""
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        return "FROM virtual_master_partner"
