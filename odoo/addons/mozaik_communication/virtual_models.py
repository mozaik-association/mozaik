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


class abstract_virtual_target(models.AbstractModel):
    _name = 'abstract.virtual.target'
    _description = 'Abstract Virtual Target'

    def fields_view_get(self, cr, uid, view_id=None, view_type='form',
                        context=None, toolbar=False, submenu=False):
        context = context or {}
        res = super(abstract_virtual_target, self).fields_view_get(
            cr, uid, view_id=view_id, view_type=view_type, context=context,
            toolbar=toolbar, submenu=submenu)
        if view_type == 'tree':
            button = etree.Element(
                'button', string='See Partner', type='object',
                name='get_partner_action', icon='gtk-redo')
            doc = etree.XML(res['arch'])
            doc.xpath('//tree')[0].append(button)
            res['arch'] = etree.tostring(doc)
        return res

    @api.multi
    def get_partner_action(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'res.partner',
            'view_mode': 'form',
            'view_type': 'form',
            'res_id': self.partner_id.id,
            'target': 'current',
        }


class virtual_target(orm.Model):
    _name = "virtual.target"
    _description = "Searching Result"
    _inherit = [
        'virtual.master.partner',
        'abstract.virtual.target',
        'abstract.term.finder'
    ]
    _auto = False

    _columns = {
        'email_coordinate_id': fields.many2one(
            'email.coordinate', string='Email Coordinate'),
        'postal_coordinate_id': fields.many2one(
            'postal.coordinate', string='Postal Coordinate'),
    }

# orm methods

    def init(self, cr):
        """
        This add an id to all columns of `virtual_master_partner`
        """
        tools.drop_view_if_exists(cr, 'virtual_target')
        cr.execute("""
        create or replace view virtual_target as (
        SELECT *,
            concat(partner_id, '/',
                   postal_coordinate_id ,'/', email_coordinate_id) as id
        FROM
            virtual_master_partner
        )""")


class virtual_partner_involvement(orm.Model):

    _name = "virtual.partner.involvement"
    _inherit = "abstract.virtual.target"
    _terms = ['interests_m2m_ids', 'competencies_m2m_ids']
    _description = "Partner/Involvement"
    _auto = False

    _columns = {
        'common_id': fields.char('Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', domain=[('is_assembly', '=', False)]),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'involvement_category_id': fields.many2one(
            'partner.involvement.category', 'Involvement Category'),

        'is_company': fields.boolean('Is a Company'),
        'identifier': fields.integer('Number', group_operator='min'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('Postal VIP'),
        'postal_unauthorized': fields.boolean('Postal Unauthorized'),

        'email_vip': fields.boolean('Email VIP'),
        'email_unauthorized': fields.boolean('Email Unauthorized'),

        'competencies_m2m_ids': fields.related(
            'partner_id', 'competencies_m2m_ids', type='many2many',
            obj='thesaurus.term', rel='res_partner_term_competencies_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related(
            'partner_id', 'interests_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_interests_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean("Active"),
        'is_donor': fields.boolean("Is a donor"),
        'is_volunteer': fields.boolean("Is a volunteer"),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_involvement')
        cr.execute("""
        create or replace view virtual_partner_involvement as (
        SELECT
            pi.id as id,
            concat(pi.partner_id, '/', pc.id, '/', e.id) as common_id,
            pi.partner_id as partner_id,
            pi.effective_time as effective_time,
            pi.promise as promise,
            pic.id as involvement_category_id,
            pic.involvement_type as involvement_type,
            p.int_instance_id as int_instance_id,
            p.local_voluntary,
            p.regional_voluntary,
            p.national_voluntary,
            p.local_only,
            p.nationality_id,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
            p.is_company as is_company,
            p.identifier as identifier,
            p.birth_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END AS active,
            p.is_donor,
            p.is_volunteer
        FROM partner_involvement AS pi

        JOIN res_partner AS p
            ON (p.id = pi.partner_id
            AND p.active = TRUE
            AND p.identifier > 0)

        JOIN partner_involvement_category AS pic
            ON (pic.id = pi.involvement_category_id
            AND pic.active = TRUE)

        LEFT OUTER JOIN postal_coordinate AS pc
            ON (pc.partner_id = p.id
            AND pc.active = TRUE
            AND pc.is_main = TRUE)

        LEFT OUTER JOIN email_coordinate AS e
            ON (e.partner_id = p.id
            AND e.active = TRUE
            AND e.is_main = TRUE)

        WHERE pi.active = TRUE
        )""")


class virtual_partner_relation(orm.Model):

    _name = "virtual.partner.relation"
    _description = "Partner/Relation"
    _inherit = "abstract.virtual.target"
    _terms = ['interests_m2m_ids', 'competencies_m2m_ids']
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one('res.partner', 'Subject'),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'relation_category_id': fields.many2one('partner.relation.category',
                                                'Relation Category'),
        'object_partner_id': fields.many2one('res.partner', 'Object'),

        'is_assembly': fields.boolean('Is an Assembly'),

        'is_company': fields.boolean('Is a Company'),
        'identifier': fields.integer('Number', group_operator='min'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

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

        'postal_vip': fields.related(
            'postal_coordinate_id', 'vip', type='boolean',
            obj='postal.coordinate', string='VIP Address'),
        'postal_unauthorized': fields.related(
            'postal_coordinate_id', 'unauthorized', type='boolean',
            obj='postal.coordinate', string='Unauthorized Address'),

        'email_vip': fields.related(
            'email_coordinate_id', 'vip', type='boolean',
            obj='email.coordinate', string='VIP Email'),
        'email_unauthorized': fields.related(
            'email_coordinate_id', 'unauthorized', type='boolean',
            obj='email.coordinate', string='Unauthorized Email'),

        'active': fields.boolean("Active"),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_relation')
        cr.execute("""
        create or replace view virtual_partner_relation as (
        SELECT
            r.id as id,
            concat(r.subject_partner_id, '/',
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
            r.subject_partner_id as partner_id,
            rc.id as relation_category_id,
            r.object_partner_id as object_partner_id,
            p.int_instance_id as int_instance_id,
            p.is_assembly as is_assembly,
            p.is_company as is_company,
            p.identifier as identifier,
            p.birth_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
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
        )""")


class virtual_partner_instance(orm.Model):

    _name = "virtual.partner.instance"
    _description = "Partner/Instance"
    _inherit = "abstract.virtual.target"
    _terms = ['interests_m2m_ids', 'competencies_m2m_ids']
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', domain=[('is_assembly', '=', False)]),
        'membership_state_id': fields.many2one('membership.state', 'State'),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'is_company': fields.boolean('Is a Company'),
        'identifier': fields.integer('Number', group_operator='min'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('VIP Address'),
        'main_postal': fields.boolean('Main Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),
        'postal_category_id': fields.many2one('coordinate.category',
                                              'Postal Coordinate Category'),

        'email_vip': fields.boolean('VIP Email'),
        'email_category_id': fields.many2one('coordinate.category',
                                             'Email Coordinate Category'),
        'main_email': fields.boolean('Main Email'),
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
        'is_donor': fields.boolean("Is a donor"),
        'is_volunteer': fields.boolean("Is a volunteer"),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_instance')
        cr.execute("""
        create or replace view virtual_partner_instance as (
        SELECT
            *,
            row_number() OVER(ORDER BY common_id) AS id
        FROM (
            SELECT
                concat(p.id, '/', pc.id, '/', e.id) as common_id,
                p.id as partner_id,
                p.int_instance_id as int_instance_id,
                e.id as email_coordinate_id,
                pc.id as postal_coordinate_id,
                pc.coordinate_category_id as postal_category_id,
                p.is_company as is_company,
                p.identifier as identifier,
                p.birth_date as birth_date,
                p.gender as gender,
                p.tongue as tongue,
                p.employee as employee,
                p.local_voluntary,
                p.regional_voluntary,
                p.national_voluntary,
                p.local_only,
                p.nationality_id,
                pc.unauthorized as postal_unauthorized,
                pc.vip as postal_vip,
                pc.is_main as main_postal,
                e.vip as email_vip,
                e.coordinate_category_id as email_category_id,
                e.is_main as main_email,
                e.unauthorized as email_unauthorized,
                ms.id as membership_state_id,
                CASE
                    WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                    THEN True
                    ELSE False
                END AS active,
                p.is_donor,
                p.is_volunteer
            FROM res_partner AS p

            LEFT OUTER JOIN membership_state AS ms
                ON (ms.id = p.membership_state_id)

            LEFT OUTER JOIN postal_coordinate AS pc
                ON (pc.partner_id = p.id
                AND pc.active = TRUE)

            LEFT OUTER JOIN email_coordinate AS e
                ON (e.partner_id = p.id
                AND e.active = TRUE)

            WHERE p.active = TRUE
            AND p.identifier > 0
            ) as subquery)
            """)


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


class virtual_assembly_instance(orm.Model):

    _name = "virtual.assembly.instance"
    _description = "Assembly/Instance"
    _inherit = "abstract.virtual.target"
    _terms = [
        'competencies_m2m_ids',
    ]
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Assembly', domain=[('is_assembly', '=', True)]),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'model': fields.char('Model'),
        'category': fields.char('Assembly Category'),

        'int_power_level_id': fields.many2one('int.power.level',
                                              'Internal Power Level'),
        'sta_power_level_id': fields.many2one('sta.power.level',
                                              'State Power Level'),

        'int_category_assembly_id': fields.many2one(
            'int.assembly.category', 'Internal Assembly Category'),
        'ext_category_assembly_id': fields.many2one(
            'ext.assembly.category', 'External Assembly Category'),
        'sta_category_assembly_id': fields.many2one(
            'sta.assembly.category', 'State Assembly Category'),

        'postal_vip': fields.boolean('VIP Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),

        'email_vip': fields.boolean('VIP Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),

        'competencies_m2m_ids': fields.related(
            'partner_id', 'competencies_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_competencies_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Topics'),
        'active': fields.boolean('Active'),
    }

# orm methods

    def _select(self, assembly_type):
        int_instance_id = ""
        if assembly_type == 'int':
            int_instance_id = 'i.id'
        elif assembly_type == 'sta':
            int_instance_id = 'i.int_instance_id'
        elif assembly_type == 'ext':
            int_instance_id = 'assembly.instance_id'

        int_cat_id = (
            "assembly.assembly_category_id"
            if assembly_type == 'int' else "NULL::int")
        sta_cat_id = (
            "assembly.assembly_category_id"
            if assembly_type == 'sta' else "NULL::int")
        ext_cat_id = (
            "assembly.assembly_category_id"
            if assembly_type == 'ext' else "NULL::int")
        int_power_id = (
            "i.power_level_id" if assembly_type == 'int' else "NULL::int")
        sta_power_id = (
            "i.power_level_id" if assembly_type == 'sta' else "NULL::int")

        return """
        SELECT
            '%s.assembly' as model,
            concat(assembly.partner_id, '/', pc.id, '/', e.id) as common_id,
            assembly.partner_id as partner_id,
            %s as int_instance_id,

            cat.name as category,

            %s as int_category_assembly_id,
            %s as sta_category_assembly_id,
            %s as ext_category_assembly_id,

            %s as int_power_level_id,
            %s as sta_power_level_id,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END AS active
        """ % (assembly_type, int_instance_id, int_cat_id, sta_cat_id,
               ext_cat_id, int_power_id, sta_power_id)

    def _from(self, assembly_type):
        instance_join = ""
        if assembly_type in ('int', 'sta'):
            instance_join = """
        JOIN %s_instance i
           ON i.id = assembly.instance_id
        """ % assembly_type

        return """
        FROM %s_assembly assembly
        JOIN res_partner AS p
            ON p.id = assembly.partner_id
        JOIN %s_assembly_category AS cat
            ON cat.id = assembly.assembly_category_id
        %s
        LEFT OUTER JOIN postal_coordinate AS pc
            ON (pc.partner_id = p.id
            AND pc.active = TRUE)
        LEFT OUTER JOIN email_coordinate AS e
            ON (e.partner_id = p.id
            AND e.active = TRUE)
        """ % (assembly_type, assembly_type, instance_join)

    def _where(self, assembly_type):
        return """
        WHERE assembly.active = TRUE
        AND p.active = TRUE
        """

    def init(self, cr):
        query_members = []
        for assembly_type in mandate_category_available_types.keys():
            query_members.append(''.join([self._select(assembly_type),
                                 self._from(assembly_type),
                                 self._where(assembly_type)]))
        query = '\nUNION\n'.join(query_members)

        tools.drop_view_if_exists(cr, 'virtual_assembly_instance')
        cr.execute("""
        create or replace view virtual_assembly_instance as (
        SELECT *, row_number() OVER(ORDER BY common_id) AS id FROM (%s) as
        subquery)""" % query)


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
            p.birth_date as birth_date,
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
            p.birth_date as birth_date,
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


class virtual_partner_membership(orm.Model):

    _name = "virtual.partner.membership"
    _description = "Partner/Membership"
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
        'membership_state_id': fields.many2one('membership.state', 'State'),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'del_doc_date': fields.date('Welcome Documents Sent Date'),
        'del_mem_card_date': fields.date('Member Card Sent Date'),

        'identifier': fields.integer('Number', group_operator='min'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),
        'reference': fields.char('Reference'),

        'postal_vip': fields.boolean('VIP Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),

        'email_vip': fields.boolean('VIP Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),

        'competencies_m2m_ids': fields.related(
            'partner_id', 'competencies_m2m_ids', type='many2many',
            obj='thesaurus.term', rel='res_partner_term_competencies_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related(
            'partner_id', 'interests_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_interests_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean('Active'),
        'is_donor': fields.boolean("Is a donor"),
        'is_volunteer': fields.boolean("Is a volunteer"),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_membership')
        cr.execute("""
        create or replace view virtual_partner_membership as (
        SELECT
            p.id as id,
            concat(p.id, '/', pc.id, '/', e.id) as common_id,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            p.del_doc_date as del_doc_date,
            p.del_mem_card_date as del_mem_card_date,
            p.reference as reference,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
            p.identifier as identifier,
            p.birth_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized,
            p.membership_state_id as membership_state_id,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END AS active,
            p.is_donor,
            p.is_volunteer
        FROM res_partner AS p
        JOIN membership_line AS m
            ON (m.partner_id = p.id
            AND m.active = TRUE)
        LEFT OUTER JOIN postal_coordinate AS pc
            ON (pc.partner_id = p.id
            AND pc.active = TRUE
            AND pc.is_main = TRUE)
        LEFT OUTER JOIN email_coordinate AS e
            ON (e.partner_id = p.id
            AND e.active = TRUE
            AND e.is_main = TRUE)
        WHERE p.active = TRUE
        )""")


class virtual_partner_event(orm.Model):

    _name = "virtual.partner.event"
    _description = "Partner/Event"
    _inherit = "abstract.virtual.target"
    _terms = [
        'competencies_m2m_ids',
        'interests_m2m_ids',
    ]
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', domain=[('identifier', '>', 0)]),
        'int_instance_id': fields.many2one(
            'int.instance', string='Internal Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'event_id': fields.many2one('event.event', 'Event'),
        'event_registration_id': fields.many2one(
            'event.registration', 'Event Registration'),

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
            obj='thesaurus.term', rel='res_partner_term_competencies_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related(
            'partner_id', 'interests_m2m_ids', type='many2many',
            obj='thesaurus.term',
            rel='res_partner_term_interests_rel',
            id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean('Active'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_event')
        cr.execute("""
        create or replace view virtual_partner_event as (
        SELECT
            er.id as id,
            concat(p.id, '/', pc.id, '/', e.id) as common_id,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
            p.identifier as identifier,
            p.birth_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized,
            er.id as event_registration_id,
            er.event_id as event_id,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END AS active
        FROM res_partner AS p

        JOIN event_registration AS er
            ON er.partner_id = p.id

        LEFT OUTER JOIN postal_coordinate AS pc
            ON (pc.partner_id = p.id
            AND pc.active = TRUE
            AND pc.is_main = TRUE)

        LEFT OUTER JOIN email_coordinate AS e
            ON (e.partner_id = p.id
            AND e.active = TRUE
            AND e.is_main = TRUE)

        WHERE p.active = TRUE
        AND p.is_company = FALSE
        )""")
