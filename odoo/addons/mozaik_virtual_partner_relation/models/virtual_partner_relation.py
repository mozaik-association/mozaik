# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerRelation(models.Model):
    _name = "virtual.partner.relation"
    _description = "Partner/Relation"
    _inherit = "abstract.virtual.target"
    _auto = False
    _terms = ['interest_ids', 'competency_ids']

    relation_category_id = fields.Many2one(
        comodel_name='res.partner.relation.type',
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
        if False:
            select = """SELECT
            CONCAT(r.left_partner_id, '/',
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
            r.left_partner_id AS partner_id,
            rc.id AS relation_category_id,
            r.right_partner_id AS object_partner_id,
            p.int_instance_id AS int_instance_id,
            p.is_assembly AS is_assembly,
            p.is_company AS is_company,
            p.identifier AS identifier,
            p.birthdate_date AS birth_date,
            p.gender AS gender,
            p.lang AS lang,
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
        else:
            select = """SELECT
            CONCAT(r.left_partner_id, '/',pc1.id,ec1.id) as common_id,
            r.left_partner_id AS partner_id,
            rc.id AS relation_category_id,
            r.right_partner_id AS object_partner_id,
            p.int_instance_id AS int_instance_id,
            p.is_assembly AS is_assembly,
            p.is_company AS is_company,
            p.identifier AS identifier,
            p.birthdate_date AS birth_date,
            p.gender AS gender,
            p.lang AS lang,
            p.employee AS employee,
            ec1.id AS email_coordinate_id,
            pc1.id AS postal_coordinate_id,
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
        from_query = """FROM res_partner_relation AS r
            JOIN res_partner AS p
                ON p.id = r.left_partner_id
                AND p.active
                AND p.identifier > 0
            JOIN res_partner_relation_type AS rc
                ON rc.id = r.type_id
            LEFT OUTER JOIN postal_coordinate AS pc1
                ON pc1.partner_id = p.id
                AND pc1.active
                AND pc1.is_main
            LEFT OUTER JOIN email_coordinate AS ec1
                ON ec1.partner_id = p.id
                AND ec1.active
                AND ec1.is_main"""
        if False:
            from_query += """
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
        return """
            WHERE (r.date_start is null OR r.date_start<=current_date)
            AND (r.date_end is null OR current_date<=r.date_end)"""
