# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from lxml import etree

from odoo import api, fields, tools, models

from odoo.addons.mozaik_person.res_partner import AVAILABLE_GENDERS
from odoo.addons.mozaik_person.res_partner import AVAILABLE_TONGUES
from odoo.addons.mozaik_retrocession.retrocession \
    import RETROCESSION_AVAILABLE_STATES
from odoo.addons.mozaik_mandate.mandate \
    import mandate_category_available_types


# Do not migrate
class virtual_partner_mandate(orm.Model):

    _name = "virtual.partner.mandate"
    _description = "Partner/Mandate"
    _inherit = "abstract.virtual.target"
    _terms = [
        'ref_partner_competencies_m2m_ids',
        'sta_competencies_m2m_ids',
        'ext_competencies_m2m_ids'
    ]
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            domain=[('is_company', '=', False), ('identifier', '>', 0)]),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'model': fields.char('Model'),

        'assembly_id': fields.many2one(
            'res.partner', 'Assembly', domain=[('is_assembly', '=', True)]),
        'mandate_category_id': fields.many2one(
            'mandate.category', string='Mandate Category'),
        'designation_int_assembly_id': fields.many2one(
            'int.assembly', string='Designation Assembly'),
        'designation_instance_id': fields.many2one(
            'int.instance', string='Designation Instance'),

        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate'),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate'),

        'ref_partner_id': fields.many2one(
            'res.partner', 'Partner'),

        'start_date': fields.date('Start Date'),
        'deadline_date': fields.date('Deadline Date'),

        'identifier': fields.integer('Number', group_operator='min'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.related(
            'postal_coordinate_id', 'vip', string='VIP Address',
            type='boolean', relation='postal.coordinate'),
        'postal_unauthorized': fields.related(
            'postal_coordinate_id', 'unauthorized',
            string='Unauthorized Address',
            type='boolean', relation='postal.coordinate'),
        'email_vip': fields.related(
            'email_coordinate_id', 'vip', string='VIP Email',
            type='boolean', relation='email.coordinate'),
        'email_unauthorized': fields.related(
            'email_coordinate_id', 'unauthorized', string='Unauthorized Email',
            type='boolean', relation='email.coordinate'),

        'ref_partner_competencies_m2m_ids': fields.related(
            'ref_partner_id', 'competencies_m2m_ids',
            type='many2many',
            obj='thesaurus.term',
            rel='ref_partner_term_competencies_rel',
            id1='ref_partner_id', id2='thesaurus_term_id',
            string='Topics'),

        'sta_competencies_m2m_ids': fields.related(
            'sta_mandate_id', 'competencies_m2m_ids',
            type='many2many',
            obj='thesaurus.term',
            rel='sta_mandate_term_competencies_rel',
            id1='sta_mandate_id', id2='thesaurus_term_id',
            string='State Mandate Remits'),
        'ext_competencies_m2m_ids': fields.related(
            'ext_mandate_id', 'competencies_m2m_ids',
            type='many2many',
            obj='thesaurus.term',
            rel='ext_mandate_term_competencies_rel',
            id1='ext_mandate_id', id2='thesaurus_term_id',
            string='External Mandate Remits'),
        'mandate_instance_id': fields.many2one(
            'int.instance', 'Mandate Instance'),
        'sta_instance_id': fields.many2one(
            'sta.instance', string='State Instance'),
        'in_progress': fields.boolean("In Progress"),
        'active': fields.boolean("Active")
    }

    def _select(self, mandate_type):
        mandate_id = (
            "mandate.id" if mandate_type == 'int' else "mandate.unique_id")
        sta_mandate_id = (
            "mandate.id" if mandate_type == 'sta' else "NULL::int")
        ext_mandate_id = (
            "mandate.id" if mandate_type == 'ext' else "NULL::int")
        mandate_instance_id = (
            "mandate.mandate_instance_id"
            if mandate_type == 'int' else "NULL::int")
        sta_instance_id = (
            "assembly.instance_id" if mandate_type == 'sta' else "NULL::int")
        ref_partner_id = (
            "assembly.ref_partner_id"
            if mandate_type == 'ext' else "NULL::int")
        return """
        SELECT '%s.mandate' AS model,
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
            %s as id,
            %s as sta_mandate_id,
            %s as ext_mandate_id,
            %s as ref_partner_id,
            mandate.mandate_category_id,
            mandate.partner_id,
            mandate.start_date,
            mandate.deadline_date,
            mandate.designation_int_assembly_id as designation_int_assembly_id,
            designation_assembly.instance_id as designation_instance_id,
            partner_assembly.id as assembly_id,
            partner.identifier as identifier,
            partner.birth_date as birth_date,
            partner.gender as gender,
            partner.tongue as tongue,
            partner.employee as employee,
            partner.int_instance_id as int_instance_id,
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
            %s as mandate_instance_id,
            %s as sta_instance_id,
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
        """ % (mandate_type, mandate_id, sta_mandate_id, ext_mandate_id,
               ref_partner_id, mandate_instance_id, sta_instance_id)

    def _from(self, mandate_type):
        return """
        FROM %s_mandate AS mandate
        JOIN %s_assembly AS assembly
            ON assembly.id = mandate.%s_assembly_id
        JOIN res_partner AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner AS partner
            ON partner.id = mandate.partner_id
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
        """ % (mandate_type, mandate_type, mandate_type)

    def _where(self, mandate_type):
        return "WHERE mandate.active = True"

# orm methods

    def init(self, cr):
        query_members = []
        for mandate_type in mandate_category_available_types.keys():
            query_members.append(''.join([self._select(mandate_type),
                                 self._from(mandate_type),
                                 self._where(mandate_type)]))
        query = '\nUNION\n'.join(query_members)

        tools.drop_view_if_exists(cr, 'virtual_partner_mandate')
        cr.execute("""
        create or replace view virtual_partner_mandate as (
        %s
        )""" % query)


# Do not migrate
class virtual_partner_candidature(orm.Model):

    _name = "virtual.partner.candidature"
    _description = "Partner/Candidature"
    _inherit = "abstract.virtual.target"
    _terms = [
        'competencies_m2m_ids',
        'interests_m2m_ids',
    ]
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            domain=[('is_company', '=', False), ('identifier', '>', 0)]),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'model': fields.char('Model'),
        'assembly_id': fields.many2one(
            'res.partner', 'Assembly', domain=[('is_assembly', '=', True)]),
        'mandate_category_id': fields.many2one('mandate.category',
                                               'Mandate Category'),
        'designation_int_assembly_id': fields.many2one(
            'int.assembly', string='Designation Assembly'),
        'designation_instance_id': fields.many2one(
            'int.instance', string='Designation Instance'),
        'sta_instance_id': fields.many2one(
            'sta.instance', string='State Instance'),

        'start_date': fields.date('Mandate Start Date'),

        'identifier': fields.integer('Number', group_operator='min'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('VIP Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),

        'email_vip': fields.boolean('VIP Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),

        'competencies_m2m_ids': fields.related(
            'partner_id', 'competencies_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_competencies_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related(
            'partner_id', 'interests_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_interests_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean("Active"),
    }

    def _select(self, cand_type):
        cand_id = ("id" if cand_type == 'int' else "unique_id")
        sta_instance_id = (
            "assembly.instance_id" if cand_type == 'sta' else "NULL::int")

        return """
        SELECT '%s.candidature' AS model,
            CONCAT(candidature.partner_id, '/', pc.id, '/', e.id) AS common_id,
            candidature.%s AS id,
            candidature.mandate_category_id,
            candidature.partner_id,
            candidature.mandate_start_date AS start_date,
            candidature.designation_int_assembly_id
                AS designation_int_assembly_id,
            designation_assembly.instance_id AS designation_instance_id,
            %s AS sta_instance_id,
            partner_assembly.id AS assembly_id,
            partner.identifier AS identifier,
            partner.birth_date AS birth_date,
            partner.gender AS gender,
            partner.tongue AS tongue,
            partner.employee AS employee,
            partner.int_instance_id AS int_instance_id,
            e.id AS email_coordinate_id,
            pc.id AS postal_coordinate_id,
            pc.unauthorized AS postal_unauthorized,
            pc.vip AS postal_vip,
            e.vip AS email_vip,
            e.unauthorized AS email_unauthorized,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END AS active
        """ % (cand_type, cand_id, sta_instance_id)

    def _from(self, cand_type):
        return """
        FROM %s_candidature AS candidature
        JOIN %s_assembly AS assembly
            ON assembly.id = candidature.%s_assembly_id
        JOIN res_partner AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner  AS partner
            ON partner.id = candidature.partner_id
        LEFT OUTER JOIN int_assembly AS designation_assembly ON
            designation_assembly.id = candidature.designation_int_assembly_id
        LEFT OUTER JOIN postal_coordinate AS pc
            ON pc.partner_id = candidature.partner_id
            and pc.is_main = TRUE
            AND pc.active = TRUE
        LEFT OUTER JOIN email_coordinate AS e
            ON e.partner_id = candidature.partner_id
            and e.is_main = TRUE
            AND e.active = TRUE
        """ % (cand_type, cand_type, cand_type)

    def _where(self, cand_type):
        return "WHERE candidature.active = True"

# orm methods

    def init(self, cr):
        query_members = []
        for cand_type in mandate_category_available_types.keys():
            query_members.append(''.join([self._select(cand_type),
                                 self._from(cand_type),
                                 self._where(cand_type)]))
        query = '\nUNION\n'.join(query_members)

        tools.drop_view_if_exists(cr, 'virtual_partner_candidature')
        cr.execute("""
        create or replace view virtual_partner_candidature as (
        %s
        )""" % query)

# Do not migrate
class virtual_partner_retrocession(orm.Model):

    _name = "virtual.partner.retrocession"
    _description = "Partner/Retrocession"
    _inherit = "abstract.virtual.target"
    _terms = [
        'competencies_m2m_ids',
        'interests_m2m_ids',
    ]
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            domain=[('is_company', '=', False), ('identifier', '>', 0)]),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'designation_int_assembly_id': fields.many2one(
            'int.assembly', string='Designation Assembly'),

        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'state': fields.selection(RETROCESSION_AVAILABLE_STATES, 'State'),

        'year': fields.char('Year'),
        'month': fields.selection(fields.date.MONTHS, 'Month',
                                  select=True, track_visibility='onchange'),

        'identifier': fields.integer('Number', group_operator='min'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate'),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate'),

        'mandate_category_id': fields.many2one('mandate.category',
                                               'Mandate Category'),

        'postal_vip': fields.related(
            'postal_coordinate_id', 'vip', string='VIP Address',
            type='boolean', relation='postal.coordinate'),
        'postal_unauthorized': fields.related(
            'postal_coordinate_id', 'unauthorized',
            string='Unauthorized Address',
            type='boolean', relation='postal.coordinate'),

        'email_vip': fields.related(
            'email_coordinate_id', 'vip', string='VIP Email',
            type='boolean', relation='email.coordinate'),
        'email_unauthorized': fields.related(
            'email_coordinate_id', 'unauthorized', string='Unauthorized Email',
            type='boolean', relation='email.coordinate'),

        'competencies_m2m_ids': fields.related(
            'partner_id', 'competencies_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_competencies_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related(
            'partner_id', 'interests_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_interests_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'retro_instance_id': fields.many2one(
            'int.instance', 'Retrocessions Management Instance'),
        'active': fields.boolean('Active'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_retrocession')
        cr.execute("""
        create or replace view virtual_partner_retrocession as (
        SELECT
            r.id as id,
            concat(p.id, '/',
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
            r.year as year,
            r.month as month,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            p.identifier as identifier,
            p.birthdate_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            m.id as sta_mandate_id,
            NULL::int as ext_mandate_id,
            m.mandate_category_id,
            m.retro_instance_id,
            m.designation_int_assembly_id as designation_int_assembly_id,
            r.state as state,
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
        FROM retrocession AS r
        JOIN sta_mandate AS m
            ON m.id = r.sta_mandate_id
            AND m.active
        JOIN res_partner AS p
            ON p.id = m.partner_id
            AND p.active = TRUE
        LEFT OUTER JOIN postal_coordinate AS pc1
            ON pc1.partner_id = p.id
            AND pc1.is_main
            AND pc1.active
        LEFT OUTER JOIN email_coordinate AS ec1
            ON ec1.partner_id = p.id
            AND ec1.is_main
            AND ec1.active
        LEFT OUTER JOIN postal_coordinate AS pc2
            ON pc2.id = m.postal_coordinate_id
            AND pc2.active
        LEFT OUTER JOIN email_coordinate AS ec2
            ON ec2.id = m.email_coordinate_id
            AND ec2.active

        UNION

        SELECT
            r.id as id,
            concat(p.id, '/',
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
            r.year as year,
            r.month as month,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            p.identifier as identifier,
            p.birthdate_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            NULL::int as sta_mandate_id,
            m.id as ext_mandate_id,
            m.mandate_category_id,
            m.retro_instance_id,
            m.designation_int_assembly_id as designation_int_assembly_id,
            r.state as state,
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
        FROM retrocession AS r
        JOIN ext_mandate AS m
            ON m.id = r.ext_mandate_id
            AND m.active
        JOIN res_partner AS p
            ON p.id = m.partner_id
            AND p.active
        LEFT OUTER JOIN postal_coordinate AS pc1
            ON pc1.partner_id = p.id
            AND pc1.is_main = True
            AND pc1.active
        LEFT OUTER JOIN email_coordinate AS ec1
            ON ec1.partner_id = p.id
            AND ec1.is_main
            AND ec1.active
        LEFT OUTER JOIN postal_coordinate AS pc2
            ON pc2.id = m.postal_coordinate_id
            AND pc2.active
        LEFT OUTER JOIN email_coordinate AS ec2
            ON ec2.id = m.email_coordinate_id
            AND ec2.active
        )""")

