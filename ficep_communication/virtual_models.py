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

from openerp.addons.ficep_person.res_partner import AVAILABLE_GENDERS, AVAILABLE_TONGUES


class virtual_target(orm.Model):

    _name = "virtual.target"
    _description = "Virtual Target"
    _auto = False

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'display_name': fields.char('Display Name'),

        'postal_coordinate_id': fields.integer('Postal Coordinate ID'),
        'email_coordinate_id': fields.integer('Email Coordinate ID'),

        'email': fields.char('Email Coordinate'),
        'postal': fields.char('Postal Coordinate'),

        'email_unauthorized': fields.boolean('Email Unauthorized'),
        'postal_unauthorized': fields.boolean('Postal Unauthorized'),

        'email_bounce_counter': fields.integer('Email Bounce Counter'),
        'postal_bounce_counter': fields.integer('Postal Bounce Counter'),

        'zip': fields.char("Zip Code"),

        'int_instance_id': fields.many2one('int.instance', 'Internal Instance'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_target')
        cr.execute("""
        create or replace view virtual_target as (
        SELECT
            concat(pc.id, '/' ,e.id) as id,
            p.id as partner_id,
            p.display_name as display_name,
            p.identifier as identification_number,

            e.bounce_counter as email_bounce_counter,
            pc.bounce_counter as postal_bounce_coutner,

            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,

            adr.zip as zip,

            e.unauthorized as email_unauthorized,
            pc.unauthorized as postal_unauthorized,

            i.id as int_instance_id,

            CASE
                WHEN pc.vip is TRUE
                THEN 'VIP'
                ELSE adr.name
            END as postal,
            CASE
                WHEN e.vip is TRUE
                THEN 'VIP'
                ELSE e.email
            END as email
        FROM
            res_partner p

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id)

        LEFT OUTER JOIN
            address_address adr
        ON (pc.address_id = adr.id)

        LEFT OUTER JOIN
            int_instance i
        ON (i.id = p.int_instance_id)

        WHERE pc.id IS NOT NULL
        OR e.id IS NOT NULL
            )""")


class virtual_partner_involvement(orm.Model):

    _name = "virtual.partner.involvement"
    _description = "Virtual Partner Involvement"
    _auto = False

    _columns = {
        'common_id': fields.char('Common ID'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'involvement_category_id': fields.many2one('partner.involvement.category', 'Involvement Category'),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'is_company': fields.boolean('Is a Company'),
        'birth_date': fields.date('Birth Date'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender'),
        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue'),
        'employee': fields.boolean('Employee'),

        'postal_vip': fields.boolean('Postal VIP'),
        'postal_unauthorized': fields.boolean('Postal Unauthorized'),

        'email_vip': fields.boolean('Email VIP'),
        'email_unauthorized': fields.boolean('Email Unauthorized'),

        #others
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
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
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
            p.birth_date as birth_date,
            p.display_name as display_name,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized
        FROM
            partner_involvement pi

        JOIN
            res_partner p
        ON (p.id = pi.partner_id
        AND p.active = TRUE)

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
        AND (pc.id IS NOT NULL
        OR e.id IS NOT NULL)
        )""")


class virtual_partner_relation(orm.Model):

    _name = "virtual.partner.relation"
    _description = "Virtual Partner Relation"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one('res.partner', 'Subject'),
        'relation_category_id': fields.many2one('partner.relation.category', 'Relation Category'),
        'object_partner_id': fields.many2one('res.partner', 'Object'),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'is_company': fields.boolean('Is a Company'),
        'is_assembly': fields.boolean('Is an Assembly'),
        'birth_date': fields.date('Birth Date'),
        'display_name': fields.char('Display Name'),
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
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),

        'postal_vip': fields.related('postal_coordinate_id', 'vip', type='boolean',
                                     obj='postal.coordinate', string='VIP Address'),
        'postal_unauthorized': fields.related('postal_coordinate_id', 'unauthorized', type='boolean',
                                     obj='postal.coordinate', string='Unauthorized Address'),

        'email_vip': fields.related('email_coordinate_id', 'vip', type='boolean',
                                     obj='email.coordinate', string='VIP Email'),
        'email_unauthorized': fields.related('email_coordinate_id', 'unauthorized', type='boolean',
                                     obj='email.coordinate', string='Unauthorized Email'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_relation')
        cr.execute("""
        create or replace view virtual_partner_relation as (
        SELECT
            r.id as id,
            concat(CASE
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
            p.is_company as is_company,
            p.is_assembly as is_assembly,
            p.birth_date as birth_date,
            p.display_name as display_name,
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
            AS postal_coordinate_id
        FROM
            partner_relation r

        JOIN
            res_partner p
        ON (p.id = r.subject_partner_id
        AND p.active = TRUE)

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
        AND (pc.id IS NOT NULL
        OR e.id IS NOT NULL
        OR r.email_coordinate_id IS NOT NULL
        OR r.postal_coordinate_id IS NOT NULL)
        )""")


class virtual_partner_instance(orm.Model):

    _name = "virtual.partner.instance"
    _description = "Virtual Partner Instance"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one('res.partner', 'Partner'),
        'int_instance_id': fields.many2one('int.instance', 'Instance'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate'),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate'),

        'is_company': fields.boolean('Is a Company'),
        'identifier': fields.integer('Number'),
        'birth_date': fields.date('Birth Date'),
        'display_name': fields.char('Display Name'),
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
                                               id1='partner_id', id2='thesaurus_term_id', string='Competencies'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_instance')
        cr.execute("""
        create or replace view virtual_partner_instance as (
        SELECT
            concat(pc.id, '/', e.id) as id,
            concat(pc.id, '/', e.id) as common_id,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
            p.is_company as is_company,
            p.birth_date as birth_date,
            p.identifier as identifier,
            p.display_name as display_name,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            pc.unauthorized as postal_unauthorized,
            pc.vip as postal_vip,
            e.vip as email_vip,
            e.unauthorized as email_unauthorized
        FROM
            res_partner p

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = TRUE)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = TRUE)

        WHERE p.active = TRUE
        AND p.is_assembly = FALSE
        AND (e.id IS NOT NULL
        OR pc.id IS NOT NULL)
        )""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
