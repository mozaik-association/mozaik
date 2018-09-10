# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, tools, models
from psycopg2.extensions import AsIs


class VirtualPartnerRelation(models.Model):
    _name = "virtual.partner.relation"
    _description = "Partner/Relation"
    _inherit = "abstract.virtual.target"
    _auto = False
    _terms = ['interests_m2m_ids', 'competencies_m2m_ids']

    common_id = fields.Char(
        string='Common ID',
    )
    partner_id = fields.Many2one('res.partner', 'Subject')
    int_instance_id = fields.Many2one(
            'int.instance', string='Internal Instance')
    email_coordinate_id = fields.Many2one('email.coordinate',
                                               'Email Coordinate')
    postal_coordinate_id = fields.Many2one('postal.coordinate',
                                                'Postal Coordinate')

    relation_category_id = fields.Many2one('partner.relation.category',
                                                'Relation Category')
    object_partner_id = fields.Many2one('res.partner', 'Object')

    is_assembly = fields.Boolean('Is an Assembly')

    is_company = fields.Boolean('Is a Company')
    identifier = fields.Integer('Number', group_operator='min')
    birth_date = fields.date('Birth Date')
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
    employee = fields.Boolean('Employee')

    competencies_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Competencies',
        related='partner_id.competencies_m2m_ids',
    )
    interests_m2m_ids = fields.Many2many(
        comodel_name='thesaurus.term',
        string='Interests',
        related='partner_id.interests_m2m_ids',
    )
    postal_vip = fields.Boolean(
        string='VIP Address',
        related='postal_coordinate_id.vip',
    )
    postal_unauthorized = fields.Boolean(
        string='Unauthorized Address',
        related='postal_coordinate_id.unauthorized',
    )
    email_vip = fields.Boolean(
        string='VIP Email',
        related='email_coordinate_id.vip',
    )
    email_unauthorized = fields.Boolean(
        string='Unauthorized Email',
        related='email_coordinate_id.unauthorized',
    )
    active = fields.Boolean("Active")

    @api.model_cr
    def init(self):
        cr = self.env.cr
        view_name = self._table
        tools.drop_view_if_exists(cr, view_name)
        query = """
CREATE OR REPLACE VIEW %(table_name)s AS (
SELECT
    r.id AS id,
    CONCAT(r.subject_partner_id, '/',
           CASE
               WHEN pc2.id IS NULL
               THEN pc1.id
               ELSE pc2.id
           END,
           '/',
           CASE
               WHEN ec2.id IS NULL
               THEN ec1.id
               ELSE ec2.id
           END) as common_id,
    r.subject_partner_id AS partner_id,
    rc.id AS relation_category_id,
    r.object_partner_id AS object_partner_id,
    p.int_instance_id AS int_instance_id,
    p.is_assembly AS is_assembly,
    p.is_company AS is_company,
    p.identifier AS identifier,
    p.birth_date AS birth_date,
    p.gender AS gender,
    p.tongue AS tongue,
    p.employee AS employee,
    CASE
        WHEN ec2.id IS NULL
        THEN ec1.id
        ELSE ec2.id
    END
    AS email_coordinate_id,
    CASE
        WHEN pc2.id IS NULL
        THEN pc1.id
        ELSE pc2.id
    END
    AS postal_coordinate_id,
    CASE
        WHEN ec1.id IS NOT NULL OR pc1.id IS NOT NULL
        THEN True
        ELSE False
    END AS active
FROM partner_relation AS r

JOIN res_partner AS p
    ON p.id = r.subject_partner_id
    AND p.active
    AND p.identifier > 0

JOIN partner_relation_category AS rc
    ON rc.id = r.partner_relation_category_id
    AND rc.active

LEFT OUTER JOIN postal_coordinate AS pc1
    ON pc1.partner_id = p.id
    AND pc1.active
    AND pc1.is_main

LEFT OUTER JOIN email_coordinate AS ec1
    ON ec1.partner_id = p.id
    AND ec1.active
    AND ec1.is_main

LEFT OUTER JOIN postal_coordinate AS pc2
    ON pc2.id = r.postal_coordinate_id
    AND pc2.active

LEFT OUTER JOIN email_coordinate AS ec2
    ON ec2.id = r.email_coordinate_id
    AND ec2.active

WHERE r.active
)"""
        query_values = {
            "table_name": AsIs(view_name),
        }
        cr.execute(query, query_values)
