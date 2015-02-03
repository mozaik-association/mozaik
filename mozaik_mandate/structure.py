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
from openerp.osv import orm, fields
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT,\
    DEFAULT_SERVER_DATETIME_FORMAT
from datetime import datetime as dt


class legislature(orm.Model):
    _name = 'legislature'
    _inherit = 'legislature'

    def write(self, cr, uid, ids, vals, context=None):
        new_deadline_date = vals.get('deadline_date', False)
        if new_deadline_date:
            for legis in self.browse(cr, uid, ids, context=context):
                if legis.deadline_date != new_deadline_date:
                    if (dt.strptime(new_deadline_date,
                        DEFAULT_SERVER_DATE_FORMAT) <
                        dt.strptime(fields.datetime.now(),
                                    DEFAULT_SERVER_DATETIME_FORMAT)):
                        raise orm.except_orm(
                            _('Warning'),
                            _('New deadline date must be greater or'
                              ' equal than today !'))
                    mandate_obj = self.pool.get('sta.mandate')
                    mandate_ids = mandate_obj.search(
                        cr,
                        uid,
                        [('legislature_id', '=', legis.id),
                         ('deadline_date', '>', new_deadline_date)])
                    if mandate_ids:
                        mandate_obj.write(cr, uid, mandate_ids,
                                          {'deadline_date': new_deadline_date})
        return super(legislature, self).write(cr, uid, ids, vals,
                                              context=context)


class electoral_district(orm.Model):

    _name = 'electoral.district'
    _inherit = ['electoral.district']

    _columns = {
        'selection_committee_ids': fields.one2many(
                                            'sta.selection.committee',
                                            'electoral_district_id',
                                            'Selection Committees'),
    }


class sta_assembly_category(orm.Model):

    _name = 'sta.assembly.category'
    _inherit = ['sta.assembly.category']

    _columns = {
        'mandate_category_ids': fields.one2many(
                                            'mandate.category',
                                            'sta_assembly_category_id',
                                            'Mandate Categories',
                                            domain=[('active', '=', True)]),
        'mandate_category_inactive_ids': fields.one2many(
                                            'mandate.category',
                                            'sta_assembly_category_id',
                                            'Mandate Categories',
                                            domain=[('active', '=', False)]),
    }


class int_assembly_category(orm.Model):

    _name = 'int.assembly.category'
    _inherit = ['int.assembly.category']

    _columns = {
        'mandate_category_ids': fields.one2many(
                                            'mandate.category',
                                            'int_assembly_category_id',
                                            'Mandate Categories',
                                            domain=[('active', '=', True)]),
        'mandate_category_inactive_ids': fields.one2many(
                                            'mandate.category',
                                            'int_assembly_category_id',
                                            'Mandate Categories',
                                            domain=[('active', '=', False)]),
    }


class ext_assembly_category(orm.Model):

    _name = 'ext.assembly.category'
    _inherit = ['ext.assembly.category']

    _columns = {
        'mandate_category_ids': fields.one2many(
                                            'mandate.category',
                                            'ext_assembly_category_id',
                                            'Mandate Categories',
                                            domain=[('active', '=', True)]),
        'mandate_category_inactive_ids': fields.one2many(
                                            'mandate.category',
                                            'ext_assembly_category_id',
                                            'Mandate Categories',
                                            domain=[('active', '=', False)]),
    }


class sta_assembly(orm.Model):

    _name = 'sta.assembly'
    _inherit = ['sta.assembly']

    _columns = {
         'selection_committee_ids': fields.one2many(
                                            'sta.selection.committee',
                                            'assembly_id',
                                            'Selection Committees',
                                            domain=[('active', '=', True)]),
         'selection_committee_inactive_ids': fields.one2many(
                                            'sta.selection.committee',
                                            'assembly_id',
                                            'Selection Committees',
                                            domain=[('active', '=', False)]),
    }


class int_assembly(orm.Model):

    _name = 'int.assembly'
    _inherit = ['int.assembly']

    _columns = {
         'selection_committee_ids': fields.one2many(
                                            'int.selection.committee',
                                            'assembly_id',
                                            'Selection Committees',
                                            domain=[('active', '=', True)]),
         'selection_committee_inactive_ids': fields.one2many(
                                            'int.selection.committee',
                                            'assembly_id',
                                            'Selection Committees',
                                            domain=[('active', '=', False)]),
    }


class ext_assembly(orm.Model):

    _name = 'ext.assembly'
    _inherit = ['ext.assembly']

    _columns = {
         'selection_committee_ids': fields.one2many(
                                            'ext.selection.committee',
                                            'assembly_id',
                                            'Selection Committees',
                                            domain=[('active', '=', True)]),
         'selection_committee_inactive_ids': fields.one2many(
                                            'ext.selection.committee',
                                            'assembly_id',
                                            'Selection Committees',
                                            domain=[('active', '=', False)]),
    }
