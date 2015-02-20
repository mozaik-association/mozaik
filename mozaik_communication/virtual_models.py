# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#    All Rights Reserved
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import tools
from openerp.osv import orm, fields

from openerp.addons.mozaik_person.res_partner import AVAILABLE_GENDERS, AVAILABLE_TONGUES
from openerp.addons.mozaik_retrocession.retrocession import RETROCESSION_AVAILABLE_STATES


class virtual_target(orm.Model):
    _name = "virtual.target"
    _description = "Searching Result"
    _inherit = ['virtual.master.partner']
    _auto = False

# orm methods

    def init(self, cr):
        """
        ====
        init
        ====
        This view will take all the columns of `virtual.partner`
        However only the row with at least one coordinate will be take
        """
        tools.drop_view_if_exists(cr, 'virtual_target')
        cr.execute("""
        create or replace view virtual_target as (
        SELECT *,
            concat(postal_coordinate_id ,'/', email_coordinate_id) as id
        FROM
            virtual_master_partner

        WHERE email_coordinate_id IS NOT NULL
        OR postal_coordinate_id IS NOT NULL
            )""")


class virtual_partner_involvement(orm.Model):

    _name = "virtual.partner.involvement"
    _description = "Partner/Involvement"
    _auto = False

    _columns = {
        'common_id': fields.char('Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', domain=[('is_assembly', '=', False)]),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'involvement_category_id': fields.many2one('partner.involvement.category', 'Involvement Category'),

        'is_company': fields.boolean('Is a Company'),
        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('Postal VIP'),
        'postal_unauthorized': fields.boolean('Postal Unauthorized'),

        'email_vip': fields.boolean('Email VIP'),
        'email_unauthorized': fields.boolean('Email Unauthorized'),

        # others
        'category_id': fields.related('partner_id', 'category_id', type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_category_rel',
                                      id1='partner_id', id2='category_id', string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_competencies_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_interests_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean("Active")
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_involvement')
        cr.execute("""
        create or replace view virtual_partner_involvement as (
        SELECT
            pi.id as id,
            concat(pc.id, '/', e.id) as common_id,
            pi.partner_id as partner_id,
            pic.id as involvement_category_id,
            p.int_instance_id as int_instance_id,
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
            END as active
        FROM
            partner_involvement pi

        JOIN
            res_partner p
        ON (p.id = pi.partner_id
        AND p.active = TRUE
        AND p.identifier > 0)

        JOIN
            partner_involvement_category pic
        ON (pic.id = pi.partner_involvement_category_id
        AND pic.active = TRUE)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = TRUE
        AND pc.is_main = TRUE)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = TRUE
        AND e.is_main = TRUE)

        WHERE pi.active = TRUE
        )""")


class virtual_partner_relation(orm.Model):

    _name = "virtual.partner.relation"
    _description = "Partner/Relation"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one('res.partner', 'Subject'),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'relation_category_id': fields.many2one('partner.relation.category', 'Relation Category'),
        'object_partner_id': fields.many2one('res.partner', 'Object'),

        'is_assembly': fields.boolean('Is an Assembly'),

        'is_company': fields.boolean('Is a Company'),
        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        # others
        'category_id': fields.related('partner_id', 'category_id', type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_category_rel',
                                      id1='partner_id', id2='category_id', string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_competencies_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_interests_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Interests'),

        'postal_vip': fields.related('postal_coordinate_id', 'vip', type='boolean',
                                     obj='postal.coordinate', string='VIP Address'),
        'postal_unauthorized': fields.related('postal_coordinate_id', 'unauthorized', type='boolean',
                                     obj='postal.coordinate', string='Unauthorized Address'),

        'email_vip': fields.related('email_coordinate_id', 'vip', type='boolean',
                                     obj='email.coordinate', string='VIP Email'),
        'email_unauthorized': fields.related('email_coordinate_id', 'unauthorized', type='boolean',
                                     obj='email.coordinate', string='Unauthorized Email'),
        'active': fields.boolean("Active")
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_relation')
        cr.execute("""
        create or replace view virtual_partner_relation as (
        SELECT
            r.id as id,
            concat(
                   CASE
                       WHEN r.postal_coordinate_id IS NULL
                       THEN pc.id
                       ELSE r.postal_coordinate_id
                   END,
                   '/',
                   CASE
                       WHEN r.email_coordinate_id IS NULL
                       THEN e.id
                       ELSE r.email_coordinate_id
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
                WHEN r.email_coordinate_id IS NULL
                THEN e.id
                ELSE r.email_coordinate_id
            END
            AS email_coordinate_id,
            CASE
                WHEN r.postal_coordinate_id IS NULL
                THEN pc.id
                ELSE r.postal_coordinate_id
            END
            AS postal_coordinate_id,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL
                      OR r.email_coordinate_id IS NOT NULL
                      OR r.postal_coordinate_id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM
            partner_relation r

        JOIN
            res_partner p
        ON (p.id = r.subject_partner_id
        AND p.active = TRUE
        AND p.identifier > 0)

        JOIN
            partner_relation_category rc
        ON (rc.id = r.partner_relation_category_id
        AND rc.active = TRUE)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = TRUE
        AND pc.is_main = TRUE)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = TRUE
        AND e.is_main = TRUE)

        WHERE r.active = TRUE
        )""")


class virtual_partner_instance(orm.Model):

    _name = "virtual.partner.instance"
    _description = "Partner/Instance"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', domain=[('is_assembly', '=', False)]),
        'membership_state_id': fields.many2one('membership.state', 'State'),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'is_company': fields.boolean('Is a Company'),
        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('VIP Address'),
        'main_postal': fields.boolean('Main Postal'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),
        'postal_category_id': fields.many2one('coordinate.category', 'Postal Coordinate Category'),

        'email_vip': fields.boolean('VIP Email'),
        'email_category_id': fields.many2one('coordinate.category', 'Email Coordinate Category'),
        'main_email': fields.boolean('Main Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),

        # others
        'category_id': fields.related('partner_id', 'category_id', type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_category_rel',
                                      id1='partner_id', id2='category_id', string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_competencies_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_interests_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean("Active")
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_instance')
        cr.execute("""
        create or replace view virtual_partner_instance as (
        SELECT
            concat(p.id, '/', pc.id, '/', e.id) as id,
            concat(pc.id, '/', e.id) as common_id,
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
            END as active

        FROM
            res_partner p

        LEFT OUTER JOIN
            membership_state ms
        ON (ms.id = p.membership_state_id)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = TRUE)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = TRUE)

        WHERE p.active = TRUE
        AND p.identifier > 0
        )""")


class virtual_partner_mandate(orm.Model):

    _name = "virtual.partner.mandate"
    _description = "Partner/Mandate"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            domain=[('is_company', '=', False), ('identifier', '>', 0)]),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'model': fields.char('Model'),

        'assembly_id': fields.many2one(
            'res.partner', 'Assembly', domain=[('is_assembly', '=', True)]),
        'mandate_category_id': fields.many2one('mandate.category', 'Mandate Category'),

        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate'),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate'),

        'start_date': fields.date('Start Date'),
        'deadline_date': fields.date('Deadline Date'),

        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.related('postal_coordinate_id', 'vip', string='VIP Address',
                                     type='boolean', relation='postal.coordinate'),
        'postal_unauthorized': fields.related('postal_coordinate_id', 'unauthorized', string='Unauthorized Address',
                                     type='boolean', relation='postal.coordinate'),

        'email_vip': fields.related('email_coordinate_id', 'vip', string='VIP Email',
                                     type='boolean', relation='email.coordinate'),
        'email_unauthorized': fields.related('email_coordinate_id', 'unauthorized', string='Unauthorized Email',
                                     type='boolean', relation='email.coordinate'),

        # others
        'sta_competencies_m2m_ids': fields.related('sta_mandate_id', 'competencies_m2m_ids',
                                               type='many2many',
                                               obj='thesaurus.term',
                                               rel='sta_mandate_term_competencies_rel',
                                               id1='sta_mandate_id', id2='thesaurus_term_id', string='State Mandate Competencies'),
        'ext_competencies_m2m_ids': fields.related('ext_mandate_id', 'competencies_m2m_ids',
                                               type='many2many',
                                               obj='thesaurus.term',
                                               rel='ext_mandate_term_competencies_rel',
                                               id1='ext_mandate_id', id2='thesaurus_term_id', string='External Mandate Competencies'),
        'mandate_instance_id': fields.many2one('int.instance', 'Mandate Instance'),
        'active': fields.boolean("Active")
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_mandate')
        cr.execute("""
        create or replace view virtual_partner_mandate as (
        SELECT 'int.mandate' AS model,
            concat(
                CASE
                    WHEN mandate.postal_coordinate_id IS NULL
                    THEN pc.id
                    ELSE mandate.postal_coordinate_id
                END,
                '/',
                CASE
                    WHEN mandate.email_coordinate_id IS NULL
                    THEN e.id
                    ELSE mandate.email_coordinate_id
                END) as common_id,
            mandate.id as id,
            NULL::int as sta_mandate_id,
            NULL::int as ext_mandate_id,
            mandate.mandate_category_id,
            mandate.partner_id,
            mandate.start_date,
            mandate.deadline_date,
            partner_assembly.id as assembly_id,
            partner.identifier as identifier,
            partner.birth_date as birth_date,
            partner.gender as gender,
            partner.tongue as tongue,
            partner.employee as employee,
            partner.int_instance_id as int_instance_id,
            CASE
                WHEN mandate.email_coordinate_id IS NULL
                THEN e.id
                ELSE mandate.email_coordinate_id
            END
            AS email_coordinate_id,
            CASE
                WHEN mandate.postal_coordinate_id IS NULL
                THEN pc.id
                ELSE mandate.postal_coordinate_id
            END
            AS postal_coordinate_id,
            mandate.mandate_instance_id as mandate_instance_id,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM int_mandate AS mandate
        JOIN int_assembly AS assembly
            ON assembly.id = mandate.int_assembly_id
        JOIN res_partner AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner AS partner
            ON partner.id = mandate.partner_id
        LEFT OUTER JOIN postal_coordinate pc
            ON pc.partner_id = mandate.partner_id
            and pc.is_main = TRUE
            AND pc.active = TRUE
        LEFT OUTER JOIN email_coordinate e
            ON e.partner_id = mandate.partner_id
            and e.is_main = TRUE
            AND e.active = TRUE
        WHERE mandate.active = True

        UNION

        SELECT 'sta.mandate' AS model,
            concat(
                CASE
                    WHEN mandate.postal_coordinate_id IS NULL
                    THEN pc.id
                    ELSE mandate.postal_coordinate_id
                END,
                '/',
                CASE
                    WHEN mandate.email_coordinate_id IS NULL
                    THEN e.id
                    ELSE mandate.email_coordinate_id
                END) as common_id,
            mandate.unique_id as id,
            mandate.id as sta_mandate_id,
            NULL::int as ext_mandate_id,
            mandate.mandate_category_id,
            mandate.partner_id,
            mandate.start_date,
            mandate.deadline_date,
            partner_assembly.id as assembly_id,
            partner.identifier as identifier,
            partner.birth_date as birth_date,
            partner.gender as gender,
            partner.tongue as tongue,
            partner.employee as employee,
            partner.int_instance_id as int_instance_id,
            CASE
                WHEN mandate.email_coordinate_id IS NULL
                THEN e.id
                ELSE mandate.email_coordinate_id
            END
            AS email_coordinate_id,
            CASE
                WHEN mandate.postal_coordinate_id IS NULL
                THEN pc.id
                ELSE mandate.postal_coordinate_id
            END
            AS postal_coordinate_id,
            NULL as mandate_instance_id,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM sta_mandate AS mandate
        JOIN sta_assembly AS assembly
            ON assembly.id = mandate.sta_assembly_id
        JOIN res_partner AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner AS partner
            ON partner.id = mandate.partner_id
        LEFT OUTER JOIN postal_coordinate pc
            ON pc.partner_id = mandate.partner_id
            and pc.is_main = TRUE
            AND pc.active = TRUE
        LEFT OUTER JOIN email_coordinate e
            ON e.partner_id = mandate.partner_id
            and e.is_main = TRUE
            AND e.active = TRUE
        WHERE mandate.active = True

        UNION

        SELECT 'ext.mandate' AS model,
            concat(
                CASE
                    WHEN mandate.postal_coordinate_id IS NULL
                    THEN pc.id
                    ELSE mandate.postal_coordinate_id
                END,
                '/',
                CASE
                    WHEN mandate.email_coordinate_id IS NULL
                    THEN e.id
                    ELSE mandate.email_coordinate_id
                END) as common_id,
            mandate.unique_id as id,
            NULL::int as sta_mandate_id,
            mandate.id as ext_mandate_id,
            mandate.mandate_category_id,
            mandate.partner_id,
            mandate.start_date,
            mandate.deadline_date,
            partner_assembly.id as assembly_id,
            partner.identifier as identifier,
            partner.birth_date as birth_date,
            partner.gender as gender,
            partner.tongue as tongue,
            partner.employee as employee,
            partner.int_instance_id as int_instance_id,
            CASE
                WHEN mandate.email_coordinate_id IS NULL
                THEN e.id
                ELSE mandate.email_coordinate_id
            END
            AS email_coordinate_id,
            CASE
                WHEN mandate.postal_coordinate_id IS NULL
                THEN pc.id
                ELSE mandate.postal_coordinate_id
            END
            AS postal_coordinate_id,
            NULL as mandate_instance_id,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM ext_mandate AS mandate
        JOIN ext_assembly AS assembly
            ON assembly.id = mandate.ext_assembly_id
        JOIN res_partner AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner  AS partner
            ON partner.id = mandate.partner_id
        LEFT OUTER JOIN postal_coordinate pc
            ON pc.partner_id = mandate.partner_id
            and pc.is_main = TRUE
            AND pc.active = TRUE
        LEFT OUTER JOIN email_coordinate e
            ON e.partner_id = mandate.partner_id
            and e.is_main = TRUE
            AND e.active = TRUE
        WHERE mandate.active = True
        )""")


class virtual_partner_candidature(orm.Model):

    _name = "virtual.partner.candidature"
    _description = "Partner/Candidature"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            domain=[('is_company', '=', False), ('identifier', '>', 0)]),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'model': fields.char('Model'),
        'assembly_id': fields.many2one(
            'res.partner', 'Assembly', domain=[('is_assembly', '=', True)]),
        'mandate_category_id': fields.many2one('mandate.category', 'Mandate Category'),
        'designation_int_assembly_id': fields.many2one('int.assembly', string='Designation Assembly'),

        'start_date': fields.date('Mandate Start Date'),

        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('VIP Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),

        'email_vip': fields.boolean('VIP Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),

        # others
        'category_id': fields.related('partner_id', 'category_id', type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_category_rel',
                                      id1='partner_id', id2='category_id', string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_competencies_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_interests_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean("Active")
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_candidature')
        cr.execute("""
        create or replace view virtual_partner_candidature as (
        SELECT 'int.candidature' AS model,
            concat(pc.id,
                '/',
                e.id) as common_id,
            candidature.id as id,
            candidature.mandate_category_id,
            candidature.partner_id,
            candidature.mandate_start_date as start_date,
            candidature.designation_int_assembly_id as designation_int_assembly_id,
            partner_assembly.id as assembly_id,
            partner.identifier as identifier,
            partner.birth_date as birth_date,
            partner.gender as gender,
            partner.tongue as tongue,
            partner.employee as employee,
            partner.int_instance_id as int_instance_id,
            e.id AS email_coordinate_id,
            pc.id AS postal_coordinate_id,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM int_candidature AS candidature
        JOIN int_assembly AS assembly
            ON assembly.id = candidature.int_assembly_id
        JOIN res_partner  AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner  AS partner
            ON partner.id = candidature.partner_id
        LEFT OUTER JOIN postal_coordinate pc
            ON pc.partner_id = candidature.partner_id
            and pc.is_main = TRUE
            AND pc.active = TRUE
        LEFT OUTER JOIN email_coordinate e
            ON e.partner_id = candidature.partner_id
            and e.is_main = TRUE
            AND e.active = TRUE
        WHERE candidature.active = True

        UNION

        SELECT 'sta.candidature' AS model,
            concat(pc.id,
                '/',
                e.id) as common_id,
            candidature.unique_id as id,
            candidature.mandate_category_id,
            candidature.partner_id,
            candidature.mandate_start_date as start_date,
            candidature.designation_int_assembly_id as designation_int_assembly_id,
            partner_assembly.id as assembly_id,
            partner.identifier as identifier,
            partner.birth_date as birth_date,
            partner.gender as gender,
            partner.tongue as tongue,
            partner.employee as employee,
            partner.int_instance_id as int_instance_id,
            e.id AS email_coordinate_id,
            pc.id AS postal_coordinate_id,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM sta_candidature AS candidature
        JOIN sta_assembly AS assembly
            ON assembly.id = candidature.sta_assembly_id
        JOIN res_partner  AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner  AS partner
            ON partner.id = candidature.partner_id
        LEFT OUTER JOIN electoral_district ed
            ON ed.id = candidature.electoral_district_id
        LEFT OUTER JOIN postal_coordinate pc
            ON pc.partner_id = candidature.partner_id
            and pc.is_main = TRUE
            AND pc.active = TRUE
        LEFT OUTER JOIN email_coordinate e
            ON e.partner_id = candidature.partner_id
            and e.is_main = TRUE
            AND e.active = TRUE
        WHERE candidature.active = True

        UNION

        SELECT 'ext.candidature' AS model,
            concat(pc.id,
                '/',
                e.id) as common_id,
            candidature.unique_id as id,
            candidature.mandate_category_id,
            candidature.partner_id,
            candidature.mandate_start_date as start_date,
            candidature.designation_int_assembly_id as designation_int_assembly_id,
            partner_assembly.id as assembly_id,
            partner.identifier as identifier,
            partner.birth_date as birth_date,
            partner.gender as gender,
            partner.tongue as tongue,
            partner.employee as employee,
            partner.int_instance_id as int_instance_id,
            e.id AS email_coordinate_id,
            pc.id postal_coordinate_id,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized,
            CASE
                WHEN (e.id IS NOT NULL OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM ext_candidature AS candidature
        JOIN ext_assembly AS assembly
            ON assembly.id = candidature.ext_assembly_id
        JOIN res_partner  AS partner_assembly
            ON partner_assembly.id = assembly.partner_id
        JOIN res_partner  AS partner
            ON partner.id = candidature.partner_id
        LEFT OUTER JOIN postal_coordinate pc
            ON pc.partner_id = candidature.partner_id
            and pc.is_main = TRUE
            AND pc.active = TRUE
        LEFT OUTER JOIN email_coordinate e
            ON e.partner_id = candidature.partner_id
            and e.is_main = TRUE
            AND e.active = TRUE
        WHERE candidature.active = True
        )""")


class virtual_assembly_instance(orm.Model):

    _name = "virtual.assembly.instance"
    _description = "Assembly/Instance"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Assembly', domain=[('is_assembly', '=', True)]),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'model': fields.char('Model'),
        'category': fields.char('Assembly Category'),

        'int_power_level_id': fields.many2one('int.power.level', 'Internal Power Level'),
        'sta_power_level_id': fields.many2one('sta.power.level', 'State Power Level'),

        'int_category_assembly_id': fields.many2one('int.assembly.category', 'Internal Assembly Category'),
        'ext_category_assembly_id': fields.many2one('ext.assembly.category', 'External Assembly Category'),
        'sta_category_assembly_id': fields.many2one('sta.assembly.category', 'State Assembly Category'),

        'postal_vip': fields.boolean('VIP Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),

        'email_vip': fields.boolean('VIP Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),

        # others
        'category_id': fields.related('partner_id', 'category_id', type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_category_rel',
                                      id1='partner_id', id2='category_id', string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_competencies_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_interests_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'active': fields.boolean('Active')
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_assembly_instance')
        cr.execute("""
        create or replace view virtual_assembly_instance as (
        SELECT
            'int.assembly' as model,
            concat(pc.id, '/', e.id) as id,
            concat(pc.id, '/', e.id) as common_id,
            assembly.partner_id as partner_id,
            i.id as int_instance_id,

            ica.name as category,

            assembly.assembly_category_id as int_category_assembly_id,
            NULL::int as sta_category_assembly_id,
            NULL::int as ext_category_assembly_id,

            i.power_level_id as int_power_level_id,
            NULL as sta_power_level_id,

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
            END as active
        FROM int_assembly assembly
        JOIN res_partner p
            ON p.id = assembly.partner_id
        JOIN int_assembly_category ica
            ON ica.id = assembly.assembly_category_id
        JOIN int_instance i
            ON i.id = assembly.instance_id
        LEFT OUTER JOIN postal_coordinate pc
            ON (pc.partner_id = p.id
            AND pc.active = TRUE)
        LEFT OUTER JOIN email_coordinate e
            ON (e.partner_id = p.id
            AND e.active = TRUE)
        WHERE assembly.active = TRUE
        AND p.active = TRUE

        UNION

        SELECT
            'sta.assembly' as model,
            concat(pc.id, '/', e.id) as id,
            concat(pc.id, '/', e.id) as common_id,
            assembly.partner_id as partner_id,
            i.int_instance_id as int_instance_id,

            sca.name as category,

            NULL::int as int_category_assembly_id,
            assembly.assembly_category_id as sta_category_assembly_id,
            NULL::int as ext_category_assembly_id,

            NULL as int_power_level_id,
            i.power_level_id as sta_power_level_id,

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
            END as active
        FROM sta_assembly assembly
        JOIN res_partner p
            ON p.id = assembly.partner_id
        JOIN sta_assembly_category sca
            ON sca.id = assembly.assembly_category_id
        JOIN sta_instance i
            ON i.id = assembly.instance_id
        LEFT OUTER JOIN postal_coordinate pc
            ON (pc.partner_id = p.id
            AND pc.active = TRUE)
        LEFT OUTER JOIN email_coordinate e
            ON (e.partner_id = p.id
            AND e.active = TRUE)
        WHERE assembly.active = TRUE
        AND p.active = TRUE

        UNION

        SELECT
            'ext.assembly' as model,
            concat(pc.id, '/', e.id) as id,
            concat(pc.id, '/', e.id) as common_id,
            assembly.partner_id as partner_id,
            assembly.instance_id as int_instance_id,

            eca.name as category,

            NULL::int as int_category_assembly_id,
            NULL::int as sta_category_assembly_id,
            assembly.assembly_category_id as ext_category_assembly_id,

            NULL as int_power_level_id,
            NULL as sta_power_level_id,

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
            END as active
        FROM ext_assembly assembly
        JOIN res_partner p
            ON p.id = assembly.partner_id
        JOIN ext_assembly_category eca
            ON eca.id = assembly.assembly_category_id
        LEFT OUTER JOIN postal_coordinate pc
            ON (pc.partner_id = p.id
            AND pc.active = TRUE)
        LEFT OUTER JOIN email_coordinate e
            ON (e.partner_id = p.id
            AND e.active = TRUE)
        WHERE assembly.active = TRUE
        AND p.active = TRUE
        )""")


class virtual_partner_retrocession(orm.Model):

    _name = "virtual.partner.retrocession"
    _description = "Partner/Retrocession"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            domain=[('is_company', '=', False), ('identifier', '>', 0)]),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'state': fields.selection(RETROCESSION_AVAILABLE_STATES, 'State'),

        'year': fields.char('Year'),
        'month': fields.selection(fields.date.MONTHS, 'Month',
                                  select=True, track_visibility='onchange'),

        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'sta_mandate_id': fields.many2one('sta.mandate', 'State Mandate'),
        'ext_mandate_id': fields.many2one('ext.mandate', 'External Mandate'),

        'mandate_category_id': fields.many2one('mandate.category', 'Mandate Category'),

        'postal_vip': fields.related('postal_coordinate_id', 'vip', string='VIP Address',
                                     type='boolean', relation='postal.coordinate'),
        'postal_unauthorized': fields.related('postal_coordinate_id', 'unauthorized', string='Unauthorized Address',
                                     type='boolean', relation='postal.coordinate'),

        'email_vip': fields.related('email_coordinate_id', 'vip', string='VIP Email',
                                     type='boolean', relation='email.coordinate'),
        'email_unauthorized': fields.related('email_coordinate_id', 'unauthorized', string='Unauthorized Email',
                                     type='boolean', relation='email.coordinate'),


        # others
        'category_id': fields.related('partner_id', 'category_id', type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_category_rel',
                                      id1='partner_id', id2='category_id', string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_competencies_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id', 'competencies_m2m_ids', type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_interests_rel',
                                               id1='partner_id', id2='thesaurus_term_id', string='Interests'),
        'retro_instance_id': fields.many2one('int.instance', 'Retrocessions Management Instance'),
        'active': fields.boolean('Active')
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_retrocession')
        cr.execute("""
        create or replace view virtual_partner_retrocession as (
        SELECT
            concat(
                r.id,
                '/',
                CASE
                    WHEN m.postal_coordinate_id IS NULL
                    THEN pc.id
                    ELSE m.postal_coordinate_id
                END,
                '/',
                CASE
                    WHEN m.email_coordinate_id IS NULL
                    THEN e.id
                    ELSE m.email_coordinate_id
                END) as id,
            concat(
                CASE
                    WHEN m.postal_coordinate_id IS NULL
                    THEN pc.id
                    ELSE m.postal_coordinate_id
                END,
                '/',
                CASE
                    WHEN m.email_coordinate_id IS NULL
                    THEN e.id
                    ELSE m.email_coordinate_id
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
            r.state as state,
            CASE
                WHEN m.email_coordinate_id IS NULL
                THEN e.id
                ELSE m.email_coordinate_id
            END
            AS email_coordinate_id,
            CASE
                WHEN m.postal_coordinate_id IS NULL
                THEN pc.id
                ELSE m.postal_coordinate_id
            END
            AS postal_coordinate_id,
            CASE
                WHEN (e.id IS NOT NULL
                       OR pc.id IS NOT NULL
                       or m.postal_coordinate_id is not null
                       or m.email_coordinate_id is not null)
                THEN True
                ELSE False
            END as active
        FROM
            retrocession r
        JOIN sta_mandate m
            ON (m.id = r.sta_mandate_id
            AND m.active = True)
        JOIN res_partner p
            ON (p.id = m.partner_id
            AND p.active = TRUE)
        LEFT OUTER JOIN
            postal_coordinate pc
            ON (pc.partner_id = p.id
            AND pc.is_main = True
            AND pc.active = True)
        LEFT OUTER JOIN
            email_coordinate e
            ON (e.partner_id = p.id
            AND e.is_main = True
            AND e.active = True)

        UNION

        SELECT
            concat(
                r.id,
                '/',
                CASE
                    WHEN m.postal_coordinate_id IS NULL
                    THEN pc.id
                    ELSE m.postal_coordinate_id
                END,
                '/',
                CASE
                    WHEN m.email_coordinate_id IS NULL
                    THEN e.id
                    ELSE m.email_coordinate_id
                END) as id,
            concat(
                CASE
                    WHEN m.postal_coordinate_id IS NULL
                    THEN pc.id
                    ELSE m.postal_coordinate_id
                END,
                '/',
                CASE
                    WHEN m.email_coordinate_id IS NULL
                    THEN e.id
                    ELSE m.email_coordinate_id
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
            r.state as state,
            CASE
                WHEN m.email_coordinate_id IS NULL
                THEN e.id
                ELSE m.email_coordinate_id
            END
            AS email_coordinate_id,
                CASE
                WHEN m.postal_coordinate_id IS NULL
                THEN pc.id
                ELSE m.postal_coordinate_id
            END
            AS postal_coordinate_id,
            CASE
                WHEN (e.id IS NOT NULL
                       OR pc.id IS NOT NULL
                       or m.postal_coordinate_id is not null
                       or m.email_coordinate_id is not null)
                THEN True
                ELSE False
            END as active
        FROM
            retrocession r
        JOIN ext_mandate m
            ON (m.id = r.ext_mandate_id
            AND m.active = True)
        JOIN res_partner p
            ON (p.id = m.partner_id
            AND p.active = TRUE)
        LEFT OUTER JOIN
            postal_coordinate pc
            ON (pc.partner_id = p.id
            AND pc.is_main = True
            AND pc.active = True)
        LEFT OUTER JOIN
            email_coordinate e
            ON (e.partner_id = p.id
            AND e.is_main = True
            AND e.active = True)
        )""")


class virtual_partner_membership(orm.Model):

    _name = "virtual.partner.membership"
    _description = "Partner/Membership"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner',
            domain=[('is_company', '=', False), ('identifier', '>', 0)]),
        'membership_state_id': fields.many2one('membership.state', 'State'),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'del_doc_date': fields.date('Welcome Documents Sent Date'),
        'del_mem_card_date': fields.date('Member Card Sent Date'),

        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),
        'reference': fields.char('Reference'),

        'postal_vip': fields.boolean('VIP Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),
        'postal_category_id': fields.many2one('coordinate.category',
                                              'Postal Coordinate Category'),

        'email_vip': fields.boolean('VIP Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),
        'email_category_id': fields.many2one('coordinate.category',
                                             'Email Coordinate Category'),

        # others
        'category_id': fields.related('partner_id', 'category_id',
                                      type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_\
                                          category_rel',
                                      id1='partner_id',
                                      id2='category_id',
                                      string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id',
                                               'competencies_m2m_ids',
                                               type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_\
                                                   competencies_rel',
                                               id1='partner_id',
                                               id2='thesaurus_term_id',
                                               string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id',
                                            'competencies_m2m_ids',
                                            type='many2many',
                                            obj='thesaurus.term',
                                            rel='res_partner_term_\
                                                interests_rel',
                                            id1='partner_id',
                                            id2='thesaurus_term_id',
                                            string='Interests'),
        'active': fields.boolean('Active')
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_membership')
        cr.execute("""
        create or replace view virtual_partner_membership as (
        SELECT
            concat(pc.id, '/', e.id) as id,
            concat(pc.id, '/', e.id) as common_id,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            p.del_doc_date as del_doc_date,
            p.del_mem_card_date as del_mem_card_date,
            p.reference as reference,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
            pc.coordinate_category_id as postal_category_id,
            p.identifier as identifier,
            p.birth_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.coordinate_category_id as email_category_id,
            e.unauthorized as email_unauthorized,
            p.membership_state_id as membership_state_id,
            CASE
                WHEN (e.id IS NOT NULL
                      OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM
            res_partner p

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = TRUE
        AND pc.is_main = TRUE)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = TRUE
        AND e.is_main = TRUE)

        WHERE p.active = TRUE
        AND p.is_company = FALSE
        )""")


class virtual_partner_event(orm.Model):

    _name = "virtual.partner.event"
    _description = "Partner/Event"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one(
            'res.partner', 'Partner', domain=[('identifier', '>', 0)]),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate',
                                               'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate',
                                                'Postal Coordinate'),

        'event_id': fields.many2one('event.event', 'Event'),
        'event_registration_id': fields.many2one(
            'event.registration', 'Event Registration'),

        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('VIP Address'),
        'postal_unauthorized': fields.boolean('Unauthorized Address'),
        'postal_category_id': fields.many2one('coordinate.category',
                                              'Postal Coordinate Category'),

        'email_vip': fields.boolean('VIP Email'),
        'email_unauthorized': fields.boolean('Unauthorized Email'),
        'email_category_id': fields.many2one('coordinate.category',
                                             'Email Coordinate Category'),

        # others
        'category_id': fields.related('partner_id', 'category_id',
                                      type='many2many',
                                      obj='res.partner.category',
                                      rel='res_partner_res_partner_\
                                          category_rel',
                                      id1='partner_id',
                                      id2='category_id',
                                      string='Tags'),
        'competencies_m2m_ids': fields.related('partner_id',
                                               'competencies_m2m_ids',
                                               type='many2many',
                                               obj='thesaurus.term',
                                               rel='res_partner_term_\
                                                   competencies_rel',
                                               id1='partner_id',
                                               id2='thesaurus_term_id',
                                               string='Competencies'),
        'interests_m2m_ids': fields.related('partner_id',
                                            'competencies_m2m_ids',
                                            type='many2many',
                                            obj='thesaurus.term',
                                            rel='res_partner_term_\
                                                interests_rel',
                                            id1='partner_id',
                                            id2='thesaurus_term_id',
                                            string='Interests'),
        'active': fields.boolean('Active')
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_event')
        cr.execute("""
        create or replace view virtual_partner_event as (
        SELECT
            er.id as id,
            concat(pc.id, '/', e.id) as common_id,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
            pc.coordinate_category_id as postal_category_id,
            p.identifier as identifier,
            p.birth_date as birth_date,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.coordinate_category_id as email_category_id,
            e.unauthorized as email_unauthorized,
            er.id as event_registration_id,
            er.event_id as event_id,
            CASE
                WHEN (e.id IS NOT NULL
                       OR pc.id IS NOT NULL)
                THEN True
                ELSE False
            END as active
        FROM
            res_partner p

        JOIN
            event_registration er
        ON er.partner_id = p.id

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = TRUE
        AND pc.is_main = TRUE)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = TRUE
        AND e.is_main = TRUE)

        WHERE p.active = TRUE
        AND p.is_company = FALSE
        )""")
