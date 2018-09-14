# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerInvolvement(models.Model):
    _name = "virtual.partner.involvement"
    _inherit = "abstract.virtual.target"
    _description = "Partner/Involvement"
    _auto = False
    _terms = [
        'interests_m2m_ids',
        'competencies_m2m_ids',
    ]

    partner_id = fields.Many2one(
        domain=[('is_assembly', '=', False)],
    )
    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement category",
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
        'res.country',
        'Nationality',
    )
    # Same remark here as before
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
        select = """SELECT
pi.id AS id,
CONCAT(pi.partner_id, '/', pc.id, '/', e.id) AS common_id,
pi.partner_id AS partner_id,
pi.effective_time AS effective_time,
pi.promise AS promise,
pic.id AS involvement_category_id,
pic.involvement_type AS involvement_type,
p.int_instance_id AS int_instance_id,
p.local_voluntary,
p.regional_voluntary,
p.national_voluntary,
p.local_only,
p.nationality_id,
e.id AS email_coordinate_id,
pc.id AS postal_coordinate_id,
p.is_company AS is_company,
p.identifier AS identifier,
p.birth_date AS birth_date,
p.gender AS gender,
p.tongue AS tongue,
p.employee AS employee,
pc.unauthorized AS postal_unauthorized,
pc.vip AS postal_vip,
e.vip AS email_vip,
e.unauthorized AS email_unauthorized,
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
        from_query = """FROM
partner_involvement AS pi
JOIN res_partner AS p
    ON (p.id = pi.partner_id AND p.active = TRUE AND p.identifier > 0)

JOIN partner_involvement_category AS pic
    ON (pic.id = pi.involvement_category_id AND pic.active = TRUE)

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
