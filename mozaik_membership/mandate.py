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
from openerp.tools import SUPERUSER_ID


class sta_candidature(orm.Model):

    _inherit = ['sta.candidature']

    _int_instance_store_trigger = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None: ids,
                            ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['sta.candidature'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }


class sta_mandate(orm.Model):

    _inherit = ['sta.mandate']

    _int_instance_store_trigger = {
        'sta.mandate': (lambda self, cr, uid, ids, context=None: ids,
                        ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['sta.mandate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }


class int_candidature(orm.Model):

    _inherit = ['int.candidature']

    _int_instance_store_trigger = {
        'int.candidature': (lambda self, cr, uid, ids, context=None: ids,
                            ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['int.candidature'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }


class int_mandate(orm.Model):

    _inherit = ['int.mandate']

    _int_instance_store_trigger = {
        'int.mandate': (lambda self, cr, uid, ids, context=None: ids,
                        ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['int.mandate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }


class ext_candidature(orm.Model):

    _inherit = ['ext.candidature']

    _int_instance_store_trigger = {
        'ext.candidature': (lambda self, cr, uid, ids, context=None: ids,
                            ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['ext.candidature'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }


class ext_mandate(orm.Model):

    _inherit = ['ext.mandate']

    _int_instance_store_trigger = {
        'ext.mandate': (lambda self, cr, uid, ids, context=None: ids,
                        ['partner_id'], 10),
        'res.partner': (lambda self, cr, uid, ids, context=None:
                        self.pool['ext.mandate'].search(
                            cr, SUPERUSER_ID, [('partner_id', 'in', ids)],
                            context=context),
                        ['int_instance_id'], 10),
    }

    _columns = {
        'partner_instance_id': fields.related(
            'partner_id', 'int_instance_id',
            string='Partner Internal Instance',
            type='many2one', relation='int.instance',
            select=True, readonly=True, store=_int_instance_store_trigger),
    }


class generic_mandate(orm.Model):

    _inherit = "generic.mandate"

    _columns = {
        'partner_instance_id': fields.many2one(
            'int.instance', string='Partner Internal Instance'),
    }

# orm methods

    def init(self, cr):
        tools.drop_view_if_exists(cr, 'generic_mandate')
        cr.execute("""
            create or replace view generic_mandate as (
                    SELECT 'int.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('int.mandate,', mandate.id) as mandate_ref,
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name,
                           partner.int_instance_id as partner_instance_id
                        FROM int_mandate  AS mandate
                        JOIN int_assembly AS assembly
                          ON assembly.id = mandate.int_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL

                    UNION

                    SELECT 'sta.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('sta.mandate,', mandate.id),
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name,
                           partner.int_instance_id as partner_instance_id
                        FROM sta_mandate  AS mandate
                        JOIN sta_assembly AS assembly
                          ON assembly.id = mandate.sta_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL

                    UNION

                    SELECT 'ext.mandate' AS model,
                           mandate.unique_id as id,
                           mandate.id as mandate_id,
                           concat('ext.mandate,', mandate.id),
                           mandate.mandate_category_id,
                           mandate.partner_id,
                           mandate.start_date,
                           mandate.deadline_date,
                           mandate.is_duplicate_detected,
                           mandate.is_duplicate_allowed,
                           partner.name as assembly_name,
                           partner.int_instance_id as partner_instance_id
                        FROM ext_mandate  AS mandate
                        JOIN ext_assembly AS assembly
                          ON assembly.id = mandate.ext_assembly_id
                        JOIN res_partner  AS partner
                          ON partner.id = assembly.partner_id
                        WHERE mandate.active = True
                        AND mandate.end_date is NULL
            )
        """)
