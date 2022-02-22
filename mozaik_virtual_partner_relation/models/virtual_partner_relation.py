# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models


class VirtualPartnerRelation(models.Model):
    _name = "virtual.partner.relation"
    _description = "Partner/Relation"
    _inherit = ["abstract.virtual.model"]
    _auto = False

    int_instance_id = fields.Many2one(
        store=True,
        search=None,
    )
    is_assembly = fields.Boolean(
        string="Is an Assembly",
    )
    relation_category_id = fields.Many2one(
        comodel_name="res.partner.relation.type",
        string="Relation Category",
    )
    object_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Object",
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
        p.int_instance_id,
        p.is_assembly AS is_assembly,
        r.type_id AS relation_category_id,
        r.right_partner_id AS object_partner_id"""
        )
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
                AND p.identifier IS NOT NULL AND p.identifier != '0'
           """
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
