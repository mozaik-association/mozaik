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


class virtual_target(orm.Model):

    _name = "virtual.target"
    _description = "Virtual Target"
    _auto = False

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate', readonly=True),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate', readonly=True),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_target')
        cr.execute("""
        create or replace view virtual_target as (
        SELECT
            concat(pc.id, '/' ,e.id) as id,
            p.id as partner_id,
            pc.id as postal_coordinate_id,
            e.id as email_coordinate_id
        FROM
            res_partner p
        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id)
        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id)
        WHERE pc.id IS NOT NULL
        OR e.id IS NOT NULL
            )""")


class virtual_partner_involvement(orm.Model):

    _name = "virtual.partner.involvement"
    _description = "Virtual Partner Involvement"
    _auto = False

    _columns = {
        'common_id': fields.char('Common ID', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Partner', readonly=True),
        'involvement_category_id': fields.many2one('partner.involvement.category', 'Involvement Category', readonly=True),
        'int_instance_id': fields.many2one('int.instance', 'Instance', readonly=True),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate', readonly=True),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate', readonly=True),

        'birth_date': fields.date('Birth Date', readonly=True),
        'display_name': fields.char('Display Name', readonly=True),
        'gender': fields.char('Gender', readonly=True),
        'tongue': fields.char('Tongue', readonly=True),
        'employee': fields.boolean('Employee', readonly=True),

        'postal_vip': fields.boolean('Postal VIP', readonly=True),
        'postal_unauthorized': fields.boolean('Postal Unauthorized', readonly=True),

        'email_vip': fields.boolean('Email VIP', readonly=True),
        'email_unauthorized': fields.boolean('Email Unauthorized', readonly=True),

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
            concat(p.id, pi.id) as id,
            concat(pc.id, '/', e.id) as common_id,
            pi.partner_id as partner_id,
            pic.id as involvement_category_id,
            p.int_instance_id as int_instance_id,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
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
        ON (pi.partner_id = p.id
        AND p.active = True
        AND pi.active = True)

        JOIN
            partner_involvement_category pic
        ON (pi.partner_involvement_category_id = pic.id
        AND pic.active = TRUE)

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = True
        AND pc.is_main = True
        AND pc.unauthorized = False)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = True
        AND e.is_main = True
        AND e.unauthorized = False)
        WHERE pc.id IS NOT NULL
        OR e.id IS NOT NULL
            )""")


class virtual_partner_relation(orm.Model):

    _name = "virtual.partner.relation"
    _description = "Virtual Partner Relation"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one('res.partner', 'Subject Partner', readonly=True),
        'relation_category_id': fields.many2one('partner.relation.category', 'Relation Category', readonly=True),
        'object_partner_id': fields.many2one('res.partner', 'Object Partner', readonly=True),
        'int_instance_id': fields.many2one('int.instance', 'Instance', readonly=True),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate', readonly=True),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate', readonly=True),

        'birth_date': fields.date('Birth Date', readonly=True),
        'display_name': fields.char('Display Name', readonly=True),
        'gender': fields.char('Gender', readonly=True),
        'tongue': fields.char('Tongue', readonly=True),
        'employee': fields.boolean('Employee', readonly=True),

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
                                     obj='postal.coordinate', string='Postal VIP', readonly=True),
        'postal_unauthorized': fields.related('postal_coordinate_id', 'unauthorized', type='boolean',
                                     obj='postal.coordinate', string='Postal Unauthorized', readonly=True),

        'email_vip': fields.related('email_coordinate_id', 'vip', type='boolean',
                                     obj='email.coordinate', string='Email VIP', readonly=True),
        'email_unauthorized': fields.related('email_coordinate_id', 'unauthorized', type='boolean',
                                     obj='email.coordinate', string='Email Unauthorized', readonly=True),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'virtual_partner_relation')
        cr.execute("""
        create or replace view virtual_partner_relation as (
        SELECT
            concat(p.id, r.id) as id,
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
            r.object_partner_id as object_partner_id,
            p.display_name as display_name,
            rc.id as relation_category_id,
            p.gender as gender,
            p.tongue as tongue,
            p.employee as employee,
            p.birth_date as birth_date,
            p.int_instance_id as int_instance_id,
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
        ON
            (r.subject_partner_id = p.id
            AND p.active = TRUE
            AND r.active = TRUE)
        JOIN
            partner_relation_category rc
        ON
            (r.partner_relation_category_id = rc.id
            AND rc.active = TRUE)
        LEFT OUTER JOIN
            email_coordinate e
        ON
            (e.partner_id = p.id
            AND e.is_main = TRUE
            AND e.active = TRUE)
        LEFT OUTER JOIN
            postal_coordinate pc
        ON
            (pc.partner_id = p.id
            AND pc.is_main = TRUE
            AND pc.active = TRUE)
        WHERE pc.id IS NOT NULL
        OR e.id IS NOT NULL
        OR r.email_coordinate_id IS NOT NULL
        OR r.postal_coordinate_id IS NOT NULL
            )""")


class virtual_partner_instance(orm.Model):

    _name = "virtual.partner.instance"
    _description = "Virtual Partner Instance"
    _auto = False

    _columns = {
        'common_id': fields.char(string='Common ID'),
        'partner_id': fields.many2one('res.partner', 'Subject Partner', readonly=True),
        'int_instance_id': fields.many2one('int.instance', 'Instance', readonly=True),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate', readonly=True),
        'postal_coordinate_id': fields.many2one('postal.coordinate', 'Postal Coordinate', readonly=True),

        'birth_date': fields.date('Birth Date', readonly=True),
        'display_name': fields.char('Display Name', readonly=True),
        'gender': fields.char('Gender', readonly=True),
        'tongue': fields.char('Tongue', readonly=True),
        'employee': fields.boolean('Employee', readonly=True),

        'postal_vip': fields.boolean('Postal VIP', readonly=True),
        'postal_unauthorized': fields.boolean('Postal Unauthorized', readonly=True),

        'email_vip': fields.boolean('Email VIP', readonly=True),
        'email_unauthorized': fields.boolean('Email Unauthorized', readonly=True),

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
            concat(p.id,pc.id,e.id) as id,
            concat(pc.id, '/', e.id) as common_id,
            p.id as partner_id,
            p.int_instance_id as int_instance_id,
            e.id as email_coordinate_id,
            pc.id as postal_coordinate_id,
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
            res_partner p

        LEFT OUTER JOIN
            postal_coordinate pc
        ON (pc.partner_id = p.id
        AND pc.active = True)

        LEFT OUTER JOIN
            email_coordinate e
        ON (e.partner_id = p.id
        AND e.active = True)
        WHERE p.active = True
        AND e.id IS NOT NULL
        OR pc.id IS NOT NULL
            )""")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
