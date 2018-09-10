# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, tools, models
from psycopg2.extensions import AsIs


class VirtualPartnerInvolvement(models.Model):
    _name = "virtual.partner.involvement"
    _inherit = "abstract.virtual.target"
    _description = "Partner/Involvement"
    _auto = False
    _terms = [
        'interests_m2m_ids',
        'competencies_m2m_ids',
    ]
    common_id = fields.Char(
        string="Common ID",
    )
    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        domain=[('is_assembly', '=', False)],
    )
    int_instance_id = fields.Many2one(
        comodel_name="int.instance",
        string="Internal instance",
    )
    email_coordinate_id = fields.Many2one(
        comodel_name="email.coordinate",
        string="Email coordinate",
    )
    postal_coordinate_id = fields.Many2one(
        comodel_name="postal.coordinate",
        string="Postal coordinate",
    )
    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement category",
    )
    is_company = fields.Boolean(
        string="Is a company",
    )
    identifier = fields.Integer(
        string="Number",
        group_operator="min",
    )
    birth_date = fields.Date()
    # Load dynamically selection values
    # If it doesn't work, better way is maybe the related (if selection
    # value come from the related)
    gender = fields.Selection(
        selection=lambda s: s.env['res.partner'].fields_get(
            allfields=['gender']).get('gender', {}).get('selection', [])
    )
    tongue = fields.Selection(
        selection=lambda s: s.env['res.partner'].fields_get(
            allfields=['tongue']).get('tongue', {}).get('selection', [])
    )
    employee = fields.Boolean()
    postal_vip = fields.Boolean(
        string="Postal VIP",
    )
    postal_unauthorized = fields.Boolean()
    email_vip = fields.Boolean(
        string="Email VIP",
    )
    email_unauthorized = fields.Boolean()
    competencies_m2m_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        related="partner_id.competencies_m2m_ids",
    )
    interests_m2m_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        related="partner_id.interests_m2m_ids",
    )
    active = fields.Boolean()
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

    @api.model_cr
    def init(self):
        cr = self.env.cr
        view_name = self._table
        tools.drop_view_if_exists(cr, view_name)
        query = """
CREATE OR REPLACE VIEW %(table_name)s AS (
SELECT
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
    p.is_volunteer
FROM
    partner_involvement AS pi
JOIN res_partner AS p
    ON (p.id = pi.partner_id AND p.active = TRUE AND p.identifier > 0)

JOIN partner_involvement_category AS pic
    ON (pic.id = pi.involvement_category_id AND pic.active = TRUE)

LEFT OUTER JOIN postal_coordinate AS pc
    ON (pc.partner_id = p.id AND pc.active = TRUE AND pc.is_main = TRUE)

LEFT OUTER JOIN email_coordinate AS e
    ON (e.partner_id = p.id AND e.active = TRUE AND e.is_main = TRUE)

WHERE pi.active = TRUE
)"""
        query_values = {
            "table_name": AsIs(view_name),
        }
        cr.execute(query, query_values)
