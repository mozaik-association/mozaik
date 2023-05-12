# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models

from odoo.addons.mozaik_mandate.models.mandate_category import (
    mandate_category_available_types,
)
from odoo.addons.mozaik_retrocession_mode.models.abstract_mandate import (
    RETROCESSION_MODES_AVAILABLE,
)


class VirtualPartnerMandate(models.Model):

    _inherit = "abstract.virtual.model"
    _name = "virtual.partner.mandate"
    _description = "Partner/Mandate"
    _terms = [
        "ref_partner_competency_ids",
        "sta_competencies_m2m_ids",
        "ext_competencies_m2m_ids",
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
    int_instance_ids = fields.Many2many(
        comodel_name="int.instance",
        compute="_compute_int_instance_ids",
        string="Internal Instances",
    )

    model = fields.Char()
    key_id = fields.Char(string="Unique String key for Mandates")

    assembly_id = fields.Many2one(
        comodel_name="res.partner",
        string="Assembly",
        domain=[("is_assembly", "=", True)],
    )
    mandate_category_id = fields.Many2one(
        comodel_name="mandate.category", string="Mandate Category"
    )
    with_remuneration = fields.Boolean()
    designation_int_assembly_id = fields.Many2one(
        comodel_name="int.assembly", string="Designation Assembly"
    )
    designation_instance_id = fields.Many2one(
        comodel_name="int.instance", string="Designation Instance"
    )

    sta_mandate_id = fields.Many2one(comodel_name="sta.mandate", string="State Mandate")
    int_mandate_id = fields.Many2one(
        comodel_name="int.mandate", string="Internal Mandate"
    )
    ext_mandate_id = fields.Many2one(
        comodel_name="ext.mandate", string="External Mandate"
    )

    ref_partner_id = fields.Many2one(comodel_name="res.partner", string="Partners")

    start_date = fields.Date(string="Start Date")
    deadline_date = fields.Date(string="Deadline Date")
    end_date = fields.Date(string="End Date")
    ref_partner_competency_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        compute="_compute_ref_partner_competency_ids",
        string="Topics",
        search="_search_ref_partner_competency_ids",
    )

    sta_competencies_m2m_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        compute="_compute_sta_competencies_m2m_ids",
        string="State Mandate Competences",
        search="_search_sta_competencies_m2m_ids",
    )
    ext_competencies_m2m_ids = fields.Many2many(
        comodel_name="thesaurus.term",
        compute="_compute_ext_competencies_m2m_ids",
        search="_search_ext_competencies_m2m_ids",
        string="External Mandate Competences",
    )
    sta_instance_id = fields.Many2one(
        comodel_name="sta.instance", string="State Instance"
    )
    in_progress = fields.Boolean("In Progress")
    active = fields.Boolean("Active")
    active_mandate = fields.Boolean("Active mandate")

    retrocession_mode = fields.Selection(RETROCESSION_MODES_AVAILABLE)
    notes = fields.Text()

    def _compute_int_instance_ids(self):
        self._compute_custom_related(
            "int_instance_ids", "ref_partner_id.int_instance_ids"
        )

    def _compute_ref_partner_competency_ids(self):
        self._compute_custom_related(
            "ref_partner_competency_ids", "ref_partner_id.competency_ids"
        )

    def _compute_sta_competencies_m2m_ids(self):
        self._compute_custom_related(
            "sta_competencies_m2m_ids", "sta_mandate_id.competencies_m2m_ids"
        )

    def _compute_ext_competencies_m2m_ids(self):
        self._compute_custom_related(
            "ext_competencies_m2m_ids", "ext_mandate_id.competencies_m2m_ids"
        )

    def _search_sta_competencies_m2m_ids(self, operator, value):
        return self._search_competencies_m2m_ids(operator, value, "sta")

    def _search_ext_competencies_m2m_ids(self, operator, value):
        return self._search_competencies_m2m_ids(operator, value, "ext")

    def _search_competencies_m2m_ids(self, operator, value, mandate_type):
        if operator not in ["ilike", "in", "not in"]:
            raise ValueError(_("This operator is not supported"))
        if operator == "ilike" and not isinstance(value, str):
            raise ValueError(_("value should be a string"))
        elif operator in ["in", "not in"] and not isinstance(value, list):
            raise ValueError(_("value should be a list"))
        mandate_model = "%(mandate_type)s.mandate" % {"mandate_type": mandate_type}
        mandate_field = "%(mandate_type)s_mandate_id" % {"mandate_type": mandate_type}
        auth_mandates = self.env[mandate_model].search(
            [("competencies_m2m_ids", operator, value)]
        )
        return [(mandate_field, "in", auth_mandates.ids)]

    def _search_ref_partner_competency_ids(self, operator, value):
        if operator not in ["ilike", "in", "not in"]:
            raise ValueError(_("This operator is not supported"))
        if operator == "ilike" and not isinstance(value, str):
            raise ValueError(_("value should be a string"))
        elif operator in ["in", "not in"] and not isinstance(value, list):
            raise ValueError(_("value should be a list"))
        auth_partners = self.env["res.partner"].search(
            [("competency_ids", operator, value)]
        )
        return [("ref_partner_id", "in", auth_partners.ids)]

    @api.model
    def _get_select(self):
        """
        We do not call super() in this virtual model, since we
        want to completely re-write it.
        """
        return """
        SELECT '%(mandate_type)s.mandate' AS model,
            %(sta_mandate_id)s as sta_mandate_id,
            %(int_mandate_id)s as int_mandate_id,
            %(ext_mandate_id)s as ext_mandate_id,
            %(ref_partner_id)s as ref_partner_id,
            CONCAT('%(mandate_type)s',mandate.id::varchar(255)) AS key_id,
            mandate.mandate_category_id,
            mandate.with_remuneration,
            mandate.partner_id as common_id,
            mandate.partner_id,
            mandate.start_date,
            mandate.deadline_date,
            mandate.end_date,
            mandate.retrocession_mode,
            mandate.active as active_mandate,
            mandate.notes,
            mandate.designation_int_assembly_id as designation_int_assembly_id,
            designation_assembly.instance_id as designation_instance_id,
            partner_assembly.id as assembly_id,
            p.identifier as identifier,
            p.birthdate_date as birth_date,
            p.birthdate_day,
            p.birthdate_month,
            p.gender as gender,
            p.lang as lang,
            p.is_company as is_company,
            p.employee as employee,
            %(sta_instance_id)s as sta_instance_id,
            CASE
                WHEN start_date <= current_date
                THEN True
                ELSE False
            END AS in_progress,
            CASE
                WHEN p.email IS NOT NULL OR p.address_address_id IS NOT NULL
                THEN True
                ELSE False
            END AS active
        """

    @api.model
    def _get_from(self):
        return """
        FROM %(mandate_type)s_mandate AS mandate
        JOIN %(mandate_type)s_assembly AS assembly
            ON assembly.id = mandate.%(mandate_type)s_assembly_id
        JOIN res_partner AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner AS p
            ON p.id = mandate.partner_id
        LEFT OUTER JOIN int_assembly AS designation_assembly
            ON designation_assembly.id = mandate.designation_int_assembly_id
        """

    @api.model
    def _get_where(self):
        return ""

    @api.model
    def _get_union_parameters(self):
        res = super()._get_union_parameters()
        res.extend(list(mandate_category_available_types.keys()))
        return res

    @api.model
    def _get_query_parameters(self, parameter=False):
        mandate_type = parameter

        mandate_id = "mandate.id" if mandate_type == "int" else "mandate.unique_id"
        sta_mandate_id = "mandate.id" if mandate_type == "sta" else "NULL::int"
        int_mandate_id = "mandate.id" if mandate_type == "int" else "NULL::int"
        ext_mandate_id = "mandate.id" if mandate_type == "ext" else "NULL::int"
        sta_instance_id = (
            "assembly.instance_id" if mandate_type == "sta" else "NULL::int"
        )
        ref_partner_id = (
            "assembly.ref_partner_id" if mandate_type == "ext" else "NULL::int"
        )
        return {
            "mandate_type": AsIs(mandate_type),
            "mandate_id": AsIs(mandate_id),
            "sta_mandate_id": AsIs(sta_mandate_id),
            "int_mandate_id": AsIs(int_mandate_id),
            "ext_mandate_id": AsIs(ext_mandate_id),
            "ref_partner_id": AsIs(ref_partner_id),
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
        followed by the mandate id.
        """
        return "key_id"
