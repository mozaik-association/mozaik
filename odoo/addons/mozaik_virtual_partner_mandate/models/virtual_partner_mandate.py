# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from psycopg2.extensions import AsIs
from odoo import api, fields, models
from odoo.addons.mozaik_mandate.models.mandate_category \
    import mandate_category_available_types


class VirtualPartnerMandate(models.Model):

    _inherit = 'abstract.virtual.model'
    _name = "virtual.partner.mandate"
    _description = "Partner/Mandate"
    _terms = [
        'ref_partner_competency_ids',
        'sta_competencies_m2m_ids',
        'ext_competencies_m2m_ids'
    ]
    _auto = False

    partner_id = fields.Many2one(
        comodel_name='res.partner', string='Partner',
        domain=[('is_company', '=', False), ('identifier', '>', 0)])
    int_instance_ids = fields.Many2many(
        related="ref_partner_id.int_instance_ids", string='Internal Instance')

    model = fields.Char()

    assembly_id = fields.Many2one(
        comodel_name='res.partner', string='Assembly',
        domain=[('is_assembly', '=', True)])
    mandate_category_id = fields.Many2one(
        comodel_name='mandate.category', string='Mandate Category')
    designation_int_assembly_id = fields.Many2one(
        comodel_name='int.assembly', string='Designation Assembly')
    designation_instance_id = fields.Many2one(
        comodel_name='int.instance', string='Designation Instance')

    sta_mandate_id = fields.Many2one(
        comodel_name='sta.mandate',
        string='State Mandate')
    ext_mandate_id = fields.Many2one(
        comodel_name='ext.mandate',
        string='External Mandate')

    ref_partner_id = fields.Many2one(
        comodel_name='res.partner',
        string='Partner')

    start_date = fields.Date(string='Start Date')
    deadline_date = fields.Date(string='Deadline Date')
    ref_partner_competency_ids = fields.Many2many(
        related='ref_partner_id.competency_ids',
        string='Topics')

    sta_competencies_m2m_ids = fields.Many2many(
        related='sta_mandate_id.competencies_m2m_ids',
        string='State Mandate Remits')
    ext_competencies_m2m_ids = fields.Many2many(
        related='ext_mandate_id.competencies_m2m_ids',
        string='External Mandate Remits')
    sta_instance_id = fields.Many2one(
        comodel_name='sta.instance', string='State Instance')
    in_progress = fields.Boolean("In Progress")
    active = fields.Boolean("Active")

    @api.model
    def _get_select(self):
        return """
        SELECT '%(mandate_type)s.mandate' AS model,
            concat(mandate.partner_id, '/',
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
            %(sta_mandate_id)s as sta_mandate_id,
            %(ext_mandate_id)s as ext_mandate_id,
            %(ref_partner_id)s as ref_partner_id,
            mandate.mandate_category_id,
            mandate.partner_id,
            mandate.start_date,
            mandate.deadline_date,
            mandate.designation_int_assembly_id as designation_int_assembly_id,
            designation_assembly.instance_id as designation_instance_id,
            partner_assembly.id as assembly_id,
            p.identifier as identifier,
            p.birthdate_date as birth_date,
            p.gender as gender,
            p.lang as lang,
            p.is_company as is_company,
            p.employee as employee,
            CASE
                WHEN ec2.id IS NULL
                THEN ec1.id
                ELSE ec2.id
            END AS email_coordinate_id,
            CASE
                WHEN pc2.id IS NULL
                THEN pc1.id
                ELSE pc2.id
            END AS postal_coordinate_id,
            CASE
                WHEN pc2.id IS NULL
                THEN pc1.unauthorized
                ELSE pc2.unauthorized
            END AS postal_unauthorized,
            CASE
                WHEN pc2.id IS NULL
                THEN pc1.vip
                ELSE pc2.vip
            END AS postal_vip,
            CASE
                WHEN ec2.id IS NULL
                THEN ec1.unauthorized
                ELSE ec2.unauthorized
            END AS email_unauthorized,
            CASE
                WHEN ec2.id IS NULL
                THEN ec1.vip
                ELSE ec2.vip
            END AS email_vip,
            %(sta_instance_id)s as sta_instance_id,
            CASE
                WHEN start_date <= current_date
                THEN True
                ELSE False
            END AS in_progress,
            CASE
                WHEN ec1.id IS NOT NULL OR pc1.id IS NOT NULL
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
        LEFT OUTER JOIN postal_coordinate AS pc1
            ON pc1.partner_id = mandate.partner_id
            AND pc1.is_main
            AND pc1.active
        LEFT OUTER JOIN email_coordinate AS ec1
            ON ec1.partner_id = mandate.partner_id
            AND ec1.is_main
            AND ec1.active
        LEFT OUTER JOIN postal_coordinate AS pc2
            ON pc2.id = mandate.postal_coordinate_id
            AND pc2.active
        LEFT OUTER JOIN email_coordinate AS ec2
            ON ec2.id = mandate.email_coordinate_id
            AND ec2.active
        """

    @api.model
    def _get_where(self):
        return "WHERE mandate.active = True"

    @api.model
    def _get_union_parameters(self):
        res = super()._get_union_parameters()
        res.extend(list(mandate_category_available_types.keys()))
        return res

    @api.model
    def _get_query_parameters(self, parameter=False):
        mandate_type = parameter

        mandate_id = (
            "mandate.id" if mandate_type == 'int' else "mandate.unique_id")
        sta_mandate_id = (
            "mandate.id" if mandate_type == 'sta' else "NULL::int")
        ext_mandate_id = (
            "mandate.id" if mandate_type == 'ext' else "NULL::int")
        sta_instance_id = (
            "assembly.instance_id" if mandate_type == 'sta' else "NULL::int")
        ref_partner_id = (
            "assembly.ref_partner_id"
            if mandate_type == 'ext' else "NULL::int")
        return {
            "mandate_type": AsIs(mandate_type),
            "mandate_id": AsIs(mandate_id),
            "sta_mandate_id": AsIs(sta_mandate_id),
            "ext_mandate_id": AsIs(ext_mandate_id),
            "ref_partner_id": AsIs(ref_partner_id),
            "sta_instance_id": AsIs(sta_instance_id)}

    @api.model
    def _from_virtual_target(self):
        return """
    LEFT OUTER JOIN
        virtual_target as vt
    ON
        vt.partner_id = p.id AND
        ((ec1.id IS NOT NULL AND vt.email_coordinate_id = ec1.id) OR
        (ec2.id IS NOT NULL AND vt.email_coordinate_id = ec2.id) OR
        (vt.email_coordinate_id IS NULL AND ec1.id IS NULL AND ec2.id IS NULL))
        AND
        ((pc1.id IS NOT NULL AND vt.postal_coordinate_id = pc1.id) OR
        (pc2.id IS NOT NULL AND vt.postal_coordinate_id = pc2.id) OR
        (vt.email_coordinate_id IS NULL AND pc1.id IS NULL AND pc2.id IS NULL))
            """
