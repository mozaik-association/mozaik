# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_mandate, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_mandate is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_mandate is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_mandate.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import fields as new_fields
from openerp import api
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


class int_instance(orm.Model):

    _inherit = 'int.instance'

    @api.multi
    def _get_model_ids(self, model):
        """
        Get all ids for a given model that are linked to an designation
        assembly for the current instance
        :type model: char
        :param model: model is the name of the model to make the search
        :rtype: [integer]
        :rparam: list of ids for the model `model`.
        """
        self.ensure_one()
        assembly_obj = self.env['int.assembly']
        model_obj = self.env[model]
        domain = [
            ('instance_id', '=', self.id),
            ('is_designation_assembly', '=', True)
        ]
        assembly_ids =\
            [assembly.id for assembly in assembly_obj.search(domain)]
        domain = [
            ('designation_int_assembly_id', 'in', assembly_ids),
        ]
        res_ids =\
            [object_ids.id for object_ids in model_obj.search(domain)]
        return res_ids

    @api.multi
    def get_model_action(self):
        """
        return an action for a specific model contains into the context
        """
        self.ensure_one()
        context = self.env.context
        action =\
            context.get('action') and context.get('action').split('.') or []
        model = context.get('model')
        if not model or not len(action) == 2:
            raise Warning(
                _('A model and an action for this model are required for '
                  'this operation'))

        module = action[0]
        action_name = action[1]
        res_ids = self._get_model_ids(model)
        domain = [('id', 'in', res_ids)]

        # get model's action to update its domain
        action = self.env['ir.actions.act_window'].for_xml_id(
            module, action_name)
        action['domain'] = domain
        return action

    @api.one
    def _compute_cand_mandate_count(self):
        """
        This method will set the value for
        * sta_mandate_count
        * sta_candidature_count
        * ext_mandate_count
        * int_mandate_count
        """
        self.sta_candidature_count = len(
            self._get_model_ids('sta.candidature'))
        self.ext_mandate_count = len(self._get_model_ids('sta.mandate'))
        self.int_mandate_count = len(self._get_model_ids('int.mandate'))
        self.sta_mandate_count = len(self._get_model_ids('ext.mandate'))

    sta_mandate_count = new_fields.Integer(
        compute='_compute_cand_mandate_count', type='integer',
        string='State Mandates')
    sta_candidature_count = new_fields.Integer(
        compute='_compute_cand_mandate_count', type='integer',
        string='State Candidatures')
    ext_mandate_count = new_fields.Integer(
        compute='_compute_cand_mandate_count', type='integer',
        string='External Mandates')
    int_mandate_count = new_fields.Integer(
        compute='_compute_cand_mandate_count', type='integer',
        string='Internal Mandates')
