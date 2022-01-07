# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerMembership(models.Model):
    _name = "virtual.partner.membership"
    _description = "Partner/Membership"
    _inherit = ["abstract.virtual.model"]
    _auto = False

    int_instance_id = fields.Many2one(
        store=True,
        search=None,
    )
    membership_state_id = fields.Many2one(
        comodel_name="membership.state",
        string="State",
    )
    reference = fields.Char()
    is_donor = fields.Boolean(
        string="Is a donor",
    )
    is_volunteer = fields.Boolean(
        string="Is a volunteer",
    )
    date_from = fields.Date(
        string="From",
    )
    date_to = fields.Date(string="To")
    date_creation = fields.Datetime(string="Creation date")
    paid = fields.Boolean(
        help="Define if this line is paid or not",
    )
    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Subscription",
    )
    active_membership_line = fields.Boolean(string="Active membership line")

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = (
            super()._get_select()
            + """,
            m.id as membership_id,
            m.int_instance_id,
            m.state_id as membership_state_id,
            m.reference as reference,
            m.date_from,
            m.date_to,
            m.create_date as date_creation,
            m.paid,
            m.product_id,
            m.active as active_membership_line,
            p.is_donor,
            p.is_volunteer"""
        )
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        from_query = """FROM res_partner AS p
            JOIN membership_line AS m
                ON m.partner_id = p.id
                """
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE p.active = TRUE"

    @api.model
    def _get_order_by(self):
        return "%s, %s" % (super()._get_order_by(), "membership_id")
