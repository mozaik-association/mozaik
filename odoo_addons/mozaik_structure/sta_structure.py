# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_structure, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_structure is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_structure is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_structure.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import datetime as DT

import openerp.tools as tools
from openerp.tools import SUPERUSER_ID
from openerp.osv import orm, fields
from openerp.tools.translate import _


class sta_power_level(orm.Model):

    _name = 'sta.power.level'
    _inherit = ['abstract.power.level']
    _description = 'State Power Level'

    _columns = {
        'assembly_category_ids': fields.one2many('sta.assembly.category',
                                                 'power_level_id',
                                                 'Assembly Categories'),
        'assembly_category_inactive_ids': fields.one2many(
            'sta.assembly.category',
            'power_level_id',
            'Assembly Categories',
            domain=[
                ('active', '=', False)
            ]),
    }


class sta_assembly_category(orm.Model):

    _name = 'sta.assembly.category'
    _inherit = ['abstract.assembly.category']
    _description = 'State Assembly Category'

    _columns = {
        'power_level_id': fields.many2one('sta.power.level',
                                          'State Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
        'is_legislative': fields.boolean('Legislative',
                                         track_visibility='onchange')
    }

    _defaults = {
        'is_legislative': False,
    }

    _order = 'power_level_id, name'

# constraints

    _unicity_keys = 'power_level_id, name'


class sta_instance(orm.Model):

    _name = 'sta.instance'
    _inherit = ['abstract.instance']
    _description = 'State Instance'

    def get_linked_electoral_districts(self, cr, uid, ids, context=None):
        """
        ============================
        get_linked_electoral_districts
        ============================
        Return electoral districts ids linked to sta_instance ids
        :rparam: sta_instance_ids
        :rtype: list of ids
        """
        sta_instances = self.read(cr, uid, ids, ['electoral_district_ids'],
                                  context=context)
        res_ids = []
        for sta_instance in sta_instances:
            res_ids += sta_instance['electoral_district_ids']
        return list(set(res_ids))

    _columns = {
        'parent_id': fields.many2one('sta.instance',
                                     'Parent State Instance',
                                     select=True,
                                     ondelete='restrict',
                                     track_visibility='onchange'),
        'secondary_parent_id': fields.many2one(
            'sta.instance',
            'Secondary Parent State Instance',
            select=True,
            track_visibility='onchange'),
        'power_level_id': fields.many2one('sta.power.level',
                                          'State Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
        'int_instance_id': fields.many2one('int.instance',
                                           'Internal Instance',
                                           required=True,
                                           select=True,
                                           track_visibility='onchange'),
        'identifier': fields.char('External Identifier (INS)',
                                  select=True,
                                  track_visibility='onchange'),
        'assembly_ids': fields.one2many('sta.assembly',
                                        'instance_id',
                                        'State Assemblies'),
        'assembly_inactive_ids': fields.one2many('sta.assembly',
                                                 'instance_id',
                                                 'State Assemblies',
                                                 domain=[
                                                     ('active', '=', False)
                                                 ]),
        'electoral_district_ids': fields.one2many('electoral.district',
                                                  'sta_instance_id',
                                                  'Electoral Districts'),
        'electoral_district_inactive_ids': fields.one2many(
            'electoral.district',
            'sta_instance_id',
            'Electoral Districts',
            domain=[
                ('active', '=', False)
            ]),
    }

    _defaults = {
        'int_instance_id': lambda self, cr, uid, ids, context = None:
            self.pool['int.instance'].get_default(cr, uid),
    }
# constraints

    def _check_recursion(self, cr, uid, ids, context=None):
        """
        ================
        _check_recursion
        ================
        Avoid recursion in instance tree regarding secondary_parent_id field
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        uid = SUPERUSER_ID
        return orm.Model._check_recursion(self, cr, uid, ids, context=context,
                                          parent='secondary_parent_id')

    _constraints = [
        (_check_recursion, _('You can not create recursive instances'),
         ['secondary_parent_id']),
    ]

    _sql_constraints = [
        ('unique_identifier', 'UNIQUE ( identifier )',
         'The external identifier (INS) must be unique.'),
    ]


class electoral_district(orm.Model):

    _name = 'electoral.district'
    _inherit = ['mozaik.abstract.model']
    _description = 'Electoral District'

    _instance_store_dict = {
        'electoral.district': (lambda self, cr, uid, ids, context=None:
                               ids, ['sta_instance_id'], 10),
        'sta.instance': (sta_instance.get_linked_electoral_districts,
                         ['int_instance_id'], 20),
    }
    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'sta_instance_id': fields.many2one('sta.instance',
                                           'State Instance',
                                           required=True,
                                           select=True,
                                           track_visibility='onchange'),
        'int_instance_id': fields.related('sta_instance_id',
                                          'int_instance_id',
                                          string='Internal Instance',
                                          select=True,
                                          type='many2one',
                                          relation="int.instance",
                                          store=_instance_store_dict,
                                          ),
        'assembly_id': fields.many2one('sta.assembly',
                                       'Assembly',
                                       required=True,
                                       select=True,
                                       track_visibility='onchange',
                                       domain=[('is_legislative', '=', True)]),
        'power_level_id': fields.related('assembly_id',
                                         'assembly_category_id',
                                         'power_level_id',
                                         string='Power Level',
                                         type='many2one',
                                         relation='sta.power.level'),
        'designation_int_assembly_id': fields.many2one(
            'int.assembly',
            string='Designation Assembly',
            required=True,
            select=True,
            track_visibility='onchange',
            domain=[
                ('is_designation_assembly', '=', True)
            ]),
        'assembly_category_id': fields.related(
            'assembly_id',
            'assembly_category_id',
            string='State Assembly Category',
            type='many2one',
            relation='sta.assembly.category'),
    }

# constraints
    _sql_constraints = [
        ('unique_name', 'UNIQUE ( name )',
         'The name must be unique.'),
    ]
    _unicity_keys = 'sta_instance_id, assembly_id'

# view methods: onchange, button

    def onchange_sta_instance_id(self, cr, uid, ids, sta_instance_id,
                                 context=None):
        return {
            'value': {
                'name': sta_instance_id and
                self.pool.get('sta.instance').name_get(
                    cr, uid, sta_instance_id, context=context)[0][1] or False,
                'int_instance_id': sta_instance_id and
                self.pool.get('sta.instance').read(
                    cr, uid, sta_instance_id, ['int_instance_id'],
                    context=context)['int_instance_id'] or False,
            }
        }


class legislature(orm.Model):

    _name = 'legislature'
    _inherit = ['mozaik.abstract.model']
    _description = 'Legislature'

    _columns = {
        'name': fields.char('Name',
                            size=128,
                            required=True,
                            select=True,
                            track_visibility='onchange'),
        'start_date': fields.date('Start Date',
                                  required=True,
                                  select=True,
                                  track_visibility='onchange'),
        'deadline_date': fields.date('Deadline Date',
                                     required=True,
                                     track_visibility='onchange'),
        'election_date': fields.date('Election Date',
                                     required=True,
                                     track_visibility='onchange'),
        'power_level_id': fields.many2one('sta.power.level',
                                          'Power Level',
                                          required=True,
                                          select=True,
                                          track_visibility='onchange'),
    }

    _order = 'start_date desc, name'

# constraints

    _unicity_keys = 'power_level_id, name, start_date'

    _sql_constraints = [
        ('date_check1', 'CHECK ( start_date <= deadline_date )',
         'The start date must be anterior to the deadline date.'),
        ('date_check2', 'CHECK ( election_date <= start_date )',
         'The election date must be anterior to the start date.'),
    ]

# orm methods

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        if isinstance(ids, (long, int)):
            ids = [ids]

        fmt = tools.DEFAULT_SERVER_DATE_FORMAT
        res = []
        for record in self.read(
                cr, uid, ids,
                ['name', 'start_date', 'deadline_date'],
                context=context):
            sdate = DT.datetime.strptime(record['start_date'], fmt)
            edate = DT.datetime.strptime(record['deadline_date'], fmt)
            display_name = '%s (%s-%s)' % \
                (record['name'], sdate.strftime('%Y'), edate.strftime('%Y'))
            res.append((record['id'], display_name))
        return res


class sta_assembly(orm.Model):

    _name = 'sta.assembly'
    _inherit = ['abstract.assembly']
    _description = 'State Assembly'

    def _compute_dummy(self, cursor, uid, ids, fname, arg, context=None):
        res = {}
        assemblies = self.browse(cursor, uid, ids, context=context)
        for ass in assemblies:
            fullname = '%s (%s)' % (ass.instance_id.name,
                                    ass.assembly_category_id.name)
            res[ass.id] = fullname
            self.pool['res.partner'].write(cursor, uid, ass.partner_id.id,
                                           {'name': fullname}, context=context)
        return res

    _name_store_triggers = {
        'sta.assembly': (
            lambda self, cr, uid, ids, context=None: ids, [
                'instance_id', 'assembly_category_id', ], 10),
        'sta.instance': (
            lambda self, cr, uid, ids, context=None:
            self.pool['sta.assembly'].search(
                cr, uid, [
                    ('instance_id', 'in', ids)], context=context), [
                'name', ], 10),
        'sta.assembly.category': (
            lambda self, cr, uid, ids, context=None:
            self.pool['sta.assembly'].search(
                cr, uid, [
                    ('assembly_category_id', 'in', ids)], context=context), [
                'name', ], 10),
    }

    _columns = {
        # dummy: define a dummy function to update the partner name associated
        #        to the assembly
        'dummy': fields.function(_compute_dummy,
                                 string='Dummy',
                                 type='char',
                                 store=_name_store_triggers,
                                 select=True),
        'assembly_category_id': fields.many2one('sta.assembly.category',
                                                'Assembly Category',
                                                select=True,
                                                required=True,
                                                track_visibility='onchange'),
        'instance_id': fields.many2one('sta.instance',
                                       'State Instance',
                                       select=True,
                                       required=True,
                                       track_visibility='onchange'),
        'is_legislative': fields.related('assembly_category_id',
                                         'is_legislative',
                                         string='Is Legislative',
                                         type='boolean',
                                         relation='sta.assembly.category',
                                         store=False),
        'electoral_district_ids': fields.one2many(
            'electoral.district', 'assembly_id',
            string='Abstract Candidatures',
            domain=[('active', '<=', True)]),
    }
