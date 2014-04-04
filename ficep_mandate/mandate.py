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
from openerp.osv import orm, fields, osv
from openerp.tools.translate import _

# Constants
MANDATE_CATEGORY_AVAILABLE_TYPES = [
    ('sta', 'State'),
    ('int', 'Internal'),
    ('ext', 'External'),
]

mandate_category_available_types = dict(MANDATE_CATEGORY_AVAILABLE_TYPES)

SELECTION_COMMITTEE_AVAILABLE_TYPES = [
    ('state', 'State'),
    ('internal', 'Internal'),
    ('external', 'External'),
]

selection_committee_available_types = dict(SELECTION_COMMITTEE_AVAILABLE_TYPES)


class mandate_category(orm.Model):

    _name = 'mandate.category'
    _description = "Mandate Category"
    _inherit = ['abstract.ficep.model']

    def get_linked_sta_candidature_ids(self, cr, uid, ids, context=None):
        """
        ============================
        get_linked_sta_candidature_ids
        ============================
        Return State Candidature ids linked to mandate category ids
        :rparam: sta_candidature_ids
        :rtype: list of ids
        """
        mandate_categories = self.read(cr, uid, ids, ['sta_candidature_ids'], context=context)
        res_ids = []
        for mandate_category in mandate_categories:
            res_ids += mandate_category['sta_candidature_ids']
        return list(set(res_ids))

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Name', size=128, translate=True, select=True, required=True, track_visibility='onchange'),
        'type': fields.selection(MANDATE_CATEGORY_AVAILABLE_TYPES, 'Status', readonly=True),
        'deadline_date': fields.date('Deadline Date', required=True, track_visibility='onchange'),
        'exclusive_category_m2m_ids': fields.many2many('mandate.category', 'mandate_category_mandate_category_rel', 'id', 'exclu_id',
                                                      'Exclusive Category'),
        'sta_assembly_category_id': fields.many2one('sta.assembly.category', string='State Assembly Category', track_visibility='onchange'),
        'ext_assembly_category_id': fields.many2one('ext.assembly.category', string='External Assembly Category', track_visibility='onchange'),
        'int_assembly_category_id': fields.many2one('int.assembly.category', string='Internal Assembly Category', track_visibility='onchange'),
        'int_power_level_id': fields.many2one('int.power.level', string='Internal Power Level',
                                                 required=True, track_visibility='onchange'),
        'sta_candidature_ids': fields.one2many('sta.candidature', 'mandate_category_id', 'State Candidatures'),
        'is_submission_mandate': fields.boolean('Submission to a mandate declaration'),
        'is_submission_assets': fields.boolean('Submission to an assets declaration'),
        }

    def _check_unique_name(self, cr, uid, ids, for_unlink=False, context=None):

        for category in self.browse(cr, uid, ids, context=context):
            if len(self.search(cr, uid, [('id', '!=', category.id), ('name', '=', category.name)])) > 0:
                return False
        return True

    _constraints = [
        (_check_unique_name, _('Name must be unique'),
          ['name'])
    ]

    _order = 'name'


class int_power_level(orm.Model):

    _name = 'int.power.level'
    _inherit = ['int.power.level']

    _columns = {
        'mandate_category_ids': fields.one2many('mandate.category', 'int_power_level_id', 'Mandate Categories'),
    }


class electoral_district(orm.Model):

    _name = 'electoral.district'
    _inherit = ['electoral.district']

    _columns = {
        'selection_committee_ids': fields.one2many('selection.committee', 'electoral_district_id', 'Selection committees'),
    }


class selection_committee(orm.Model):
    _name = 'selection.committee'
    _description = "Selection Committee"
    _inherit = ['abstract.ficep.model']

    def _get_suggested_sta_candidatures(self, sta_candidature_ids):
        res = []
        for candidature in sta_candidature_ids:
            if candidature.state == 'rejected':
                continue
            elif candidature.state == 'suggested':
                res.append(candidature.id)
            else:
                raise osv.except_osv(_('Operation Forbidden!'),
                             _('All candidatures are not in suggested state'))
        return res

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'committee_type': fields.selection(SELECTION_COMMITTEE_AVAILABLE_TYPES, 'Type', required=True, track_visibility='onchange',),
        'decision_date': fields.date('Decision Date', track_visibility='onchange'),
        'mandate_date': fields.date('Start date of mandate', track_visibility='onchange'),
        'name': fields.char('Name', size=128, translate=True, select=True, required=True, track_visibility='onchange'),
        'is_virtual': fields.boolean('Is virtual'),
        'partner_ids': fields.many2many('res.partner', 'selection_committee_res_partner_rel', 'id', 'member_id',
                                                      'Members', domain=[('is_company', '=', False)]),
        'sta_assembly_id': fields.many2one('sta.assembly', string='State Assembly', track_visibility='onchange'),
        'int_assembly_id': fields.many2one('int.assembly', string='Internal Assembly', track_visibility='onchange'),
        'ext_assembly_id': fields.many2one('ext.assembly', string='External Assembly', track_visibility='onchange'),
        'int_designation_assembly_id': fields.many2one('int.assembly', string='Internal Assembly (Designation)',
                                                 required=True, track_visibility='onchange'),
        'sta_candidature_ids': fields.one2many('sta.candidature', 'selection_committee_id', 'State Candidatures',
                                               domain=[('state', 'not in', ['draft', 'rejected'])]),
        'electoral_district_id': fields.many2one('electoral.district', string='Electoral District', track_visibility='onchange'),
        'legislature_id': fields.many2one('legislature', string='Legislature', track_visibility='onchange'),
        'power_level_id': fields.many2one('sta.power.level', string='Power level'),
        'int_instance_id': fields.many2one('int.instance', string='Internal Instance'),
    }

    _defaults = {
        'is_virtual': False,
        }

# orm methods
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for committee in self.browse(cr, uid, ids, context=context):
            if committee.committee_type == 'state':
                display_name = u"{name} {legislature} {electoral_district}".format(name=committee.name,
                                                                                  legislature=committee.legislature_id.name,
                                                                                  electoral_district=committee.electoral_district_id.name)
            else:
                display_name = committee.name
            res.append((committee['id'], display_name))
        return res

    def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        committee_type = context.get('committee_type', False)
        if not args:
            args = []
        if name and committee_type == 'state':
            legislature_ids = self.pool.get('legislature').search(cr, uid, [('name', operator, name)], context=context)
            district_ids = self.pool.get('electoral.district').search(cr, uid, [('name', operator, name)], context=context)
            ids = self.search(cr, uid, ['|', '|', ('name', operator, name), ('legislature_id', 'in', legislature_ids), ('electoral_district_id', 'in', district_ids)] + args, limit=limit, context=context)
        else:
            ids = self.search(cr, uid, args, limit=limit, context=context)
        return self.name_get(cr, uid, ids, context)

# view methods: onchange, button
    def button_accept_candidatures(self, cr, uid, ids, context=None):
            """
            ==========
            button_accept_candidatures
            ==========
            This method calls the candidature workflow for each candidature_id in order to update their state
            :rparam: True
            :rtype: boolean
            :raise: Error if all candidatures are not in suggested state
            """
            for committee in self.browse(cr, uid, ids, context=context):
                if committee.committee_type == 'state':
                    if committee.sta_candidature_ids:
                        self.pool.get('sta.candidature').signal_action_designate(cr, uid, self._get_suggested_sta_candidatures(committee.sta_candidature_ids))
            return True

    def button_reject_candidatures(self, cr, uid, ids, context=None):
            """
            ==========
            button_reject_candidatures
            ==========
            This method calls the candidature workflow for each candidature_id in order to update their state
            :rparam: True
            :rtype: boolean
            :raise: Error if all candidatures are not in suggested state
            """
            for committee in self.browse(cr, uid, ids, context=context):
                if committee.committee_type == 'state':
                    if committee.sta_candidature_ids:
                        self.pool.get('sta.candidature').signal_button_declare(cr, uid, self._get_suggested_sta_candidatures(committee.sta_candidature_ids))
            return True

    def onchange_committee_type(self, cr, uid, ids, committee_type, context=None):
        res = {}
        if committee_type == 'state':
            res['value'] = dict(is_virtual=False,
                                int_assembly_id=False,
                                ext_assembly_id=False,
                                power_level_id=self.pool.get("ir.model.data").get_object_reference(cr, uid, "ficep_structure", "int_power_level_01")[1])
        elif committee_type == 'internal':
            res['value'] = dict(sta_assembly_id=False,
                                ext_assembly_id=False,
                                electoral_district_id=False,
                                legislature_id=False)
        elif committee_type == 'external':
            res['value'] = dict(sta_assembly_id=False,
                                int_assembly_id=False,
                                electoral_district_id=False,
                                legislature_id=False)

        return res

    def onchange_legislature_id(self, cr, uid, ids, legislature_id, context=None):
        legislature_data = self.pool.get('legislature').read(cr, uid, legislature_id, ['power_level_id', 'create_date'])
        res = {}
        res['value'] = dict(power_level_id=legislature_data['power_level_id'],
                            mandate_date=legislature_data['create_date'],  # TODO replace by start_date
                            electoral_district_id=False)
        return res

    def onchange_electoral_district_id(self, cr, uid, ids, electoral_district_id, context=None):
        district_data = self.pool.get('electoral.district').read(cr, uid, electoral_district_id, ['int_instance_id', 'assembly_id'])
        res = {}
        res['value'] = dict(int_instance_id=district_data['int_instance_id'],
                            sta_assembly_id=district_data['assembly_id'])
        return res
