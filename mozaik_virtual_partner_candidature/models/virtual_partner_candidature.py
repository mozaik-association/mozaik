# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models

from odoo.addons.mozaik_committee.models.abstract_candidature import (
    candidature_available_types,
)


class VirtualPartnerCandidature(models.Model):
    _name = "virtual.partner.candidature"
    _inherit = "abstract.virtual.model"
    _description = "Partner/Candidature"
    _terms = [
        "competency_ids",
        "interest_ids",
    ]
    _auto = False

    partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Partner",
        domain=[
            ("is_company", "=", False),
            ("identifier", "!=", False),
            ("identifier", "!=", "0"),
        ],
    )
    model = fields.Char()
    sta_candidature_id = fields.Many2one(
        comodel_name="sta.candidature", string="State Candidature"
    )
    int_candidature_id = fields.Many2one(
        comodel_name="int.candidature", string="Internal Candidature"
    )
    ext_candidature_id = fields.Many2one(
        comodel_name="ext.candidature", string="External Candidature"
    )
    key_id = fields.Char(string="Unique String key for Candidatures")

    mandate_category_id = fields.Many2one(
        comodel_name="mandate.category", string="Mandate Category"
    )
    start_date = fields.Date(string="Start Date")
    designation_int_assembly_id = fields.Many2one(
        comodel_name="int.assembly", string="Designation Assembly"
    )
    designation_instance_id = fields.Many2one(
        comodel_name="int.instance", string="Designation Instance"
    )
    assembly_id = fields.Many2one(
        comodel_name="res.partner",
        string="Assembly",
        domain=[("is_assembly", "=", True)],
    )
    int_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        compute="_compute_int_instance_ids",
        string="Internal Instances",
    )
    sta_instance_id = fields.Many2one(
        comodel_name="sta.instance", string="State Instance"
    )
    competency_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        compute="_compute_competency_ids",
        string="Topics",
        search="_search_competency_ids",
    )
    interest_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        compute="_compute_interest_ids",
        string="Interests",
        search="_search_interest_ids",
    )
    active_candidature = fields.Boolean("Active candidature")

    def _compute_int_instance_ids(self):
        self._compute_custom_related("int_instance_ids", "partner_id.int_instance_ids")

    def _compute_competency_ids(self):
        self._compute_custom_related("competency_ids", "partner_id.competency_ids")

    def _compute_interest_ids(self):
        self._compute_custom_related("interest_ids", "partner_id.interest_ids")

    def _validate_operator_value(self, operator, value):
        if operator not in ["ilike", "in", "not in"]:
            raise ValueError(_("This operator is not supported"))
        if operator == "ilike" and not isinstance(value, str):
            raise ValueError(_("value should be a string"))
        elif operator in ["in", "not in"] and not isinstance(value, list):
            raise ValueError(_("value should be a list"))

    def _search_competency_ids(self, operator, value):
        self._validate_operator_value(operator, value)
        auth_partners = self.env["res.partner"].search(
            [("competency_ids", operator, value)]
        )
        return [("partner_id", "in", auth_partners.ids)]

    def _search_interest_ids(self, operator, value):
        self._validate_operator_value(operator, value)
        auth_partners = self.env["res.partner"].search(
            [("interest_ids", operator, value)]
        )
        return [("partner_id", "in", auth_partners.ids)]

    @api.model
    def _get_select(self):
        """
        We do not call super() in this virtual model, since we
        want to completely re-write it.
        """
        return """SELECT '%(cand_type)s.candidature' AS model,
            %(sta_cand_id)s as sta_candidature_id,
            %(int_cand_id)s as int_candidature_id,
            %(ext_cand_id)s as ext_candidature_id,
            CONCAT('%(cand_type)s',cand.id::varchar(255)) AS key_id,
            cand.partner_id AS common_id,
            cand.partner_id AS partner_id,
            cand.mandate_category_id,
            cand.mandate_start_date AS start_date,
            cand.active AS active_candidature,
            cand.designation_int_assembly_id AS designation_int_assembly_id,
            designation_assembly.instance_id AS designation_instance_id,
            partner_assembly.id AS assembly_id,
            %(sta_instance_id)s as sta_instance_id,
            p.identifier AS identifier,
            p.birthdate_date AS birth_date,
            p.birthdate_day,
            p.birthdate_month,
            p.gender AS gender,
            p.lang AS lang,
            p.employee AS employee,
            CASE
                WHEN p.email IS NOT NULL OR p.address_address_id IS NOT NULL
                THEN True
                ELSE False
            END AS active"""

    @api.model
    def _get_from(self):
        return """
            FROM %(cand_type)s_candidature AS cand
            JOIN %(cand_type)s_assembly AS assembly
                ON assembly.id = cand.%(cand_type)s_assembly_id
            JOIN res_partner AS partner_assembly
                ON partner_assembly.id = assembly.partner_id
            JOIN res_partner AS p
                ON p.id = cand.partner_id
            LEFT OUTER JOIN int_assembly AS designation_assembly
                ON designation_assembly.id = cand.designation_int_assembly_id
            """

    @api.model
    def _get_where(self):
        """
        Build the WHERE of the SQL query
        :return: str
        """
        return "WHERE cand.active = TRUE"

    @api.model
    def _get_union_parameters(self):
        res = super()._get_union_parameters()
        res.extend(list(candidature_available_types.keys()))
        return res

    @api.model
    def _get_query_parameters(self, parameter=False):
        cand_type = parameter
        sta_cand_id = "cand.id" if cand_type == "sta" else "NULL::int"
        int_cand_id = "cand.id" if cand_type == "int" else "NULL::int"
        ext_cand_id = "cand.id" if cand_type == "ext" else "NULL::int"
        sta_instance_id = "assembly.instance_id" if cand_type == "sta" else "NULL::int"
        return {
            "cand_type": AsIs(cand_type),
            "sta_cand_id": AsIs(sta_cand_id),
            "int_cand_id": AsIs(int_cand_id),
            "ext_cand_id": AsIs(ext_cand_id),
            "sta_instance_id": AsIs(sta_instance_id),
        }

    @api.model
    def _get_order_by(self):
        """
        Since several records can have the same partner_id,
        ORDER BY 'partner_id' doesn't give always the same
        ordering between records having the same partner_id.
        We thus need to find a unique way to determine the ids
        and order the records.
        We built a key_id which is a string made with prefix 'int', 'sta' or 'ext'
        followed by the candidature id.
        """
        return "key_id"
