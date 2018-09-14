# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerRelation(models.Model):
    _name = "virtual.partner.relation"
    _description = "Partner/Relation"
    _inherit = "abstract.virtual.target"
    _auto = False
    _terms = ['interests_m2m_ids', 'competencies_m2m_ids']

    relation_category_id = fields.Many2one(
        comodel_name='partner.relation.category',
        string='Relation Category',
    )
    object_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Object',
    )
    is_assembly = fields.Boolean(
        string='Is an Assembly',
    )
    postal_unauthorized = fields.Boolean(
        related='postal_coordinate_id.unauthorized',
    )
    email_vip = fields.Boolean(
        related='email_coordinate_id.vip',
    )
    email_unauthorized = fields.Boolean(
        related='email_coordinate_id.unauthorized',
    )

    @api.model
    def _get_select(self):
        """
        Build the SELECT of the SQL query
        :return: str
        """
        select = """SELECT
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
            END AS active"""
        return select

    @api.model
    def _get_from(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        from_query = """FROM partner_relation AS r
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
                AND ec2.active"""
        return from_query

    @api.model
    def _get_where(self):
        """
        Build the FROM of the SQL query
        :return: str
        """
        return "WHERE r.active"
