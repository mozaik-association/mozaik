# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerInvolvement(models.Model):
    _name = "virtual.partner.involvement"
    _inherit = "abstract.virtual.model"
    _description = "Partner/Involvement"
    _auto = False
    _terms = [
        'interest_ids',
        'competency_ids',
    ]

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
        'res.country',
        'Nationality',
    )
    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement Category",
    )
    involvement_type = fields.Selection(
        selection=lambda s: s.env['partner.involvement.category'].fields_get(
            allfields=['involvement_type']).get(
                'involvement_type', {}).get('selection', [])
    )
    effective_time = fields.Datetime(
        'Involvement Date',
    )
    promise = fields.Boolean()

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
            pi.involvement_category_id,
            pi.involvement_type,
            pi.effective_time AS effective_time,
            pi.promise AS promise"""
        return select

    @api.model
    def _get_from(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        from_query = """FROM
partner_involvement AS pi
JOIN res_partner AS p
    ON (p.id = pi.partner_id AND p.active = TRUE AND p.identifier > 0)

LEFT OUTER JOIN postal_coordinate AS pc
    ON (pc.partner_id = p.id AND pc.active = TRUE AND pc.is_main = TRUE)

LEFT OUTER JOIN email_coordinate AS e
    ON (e.partner_id = p.id AND e.active = TRUE AND e.is_main = TRUE)"""
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE pi.active = TRUE"
