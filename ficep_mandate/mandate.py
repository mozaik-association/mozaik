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

SELECTION_COMMITTEE_AVAILABLE_STATES = [
    ('draft', 'In Progress'),
    ('done', 'Closed'),
]
selection_committee_available_states = dict(SELECTION_COMMITTEE_AVAILABLE_STATES)


class mandate_category(orm.Model):

    _name = 'mandate.category'
    _description = 'Mandate Category'
    _inherit = ['abstract.ficep.model']

    def get_linked_sta_mandate_ids(self, cr, uid, ids, context=None):
        """
        ==============================
        get_linked_mandate_ids
        ==============================
        Return State Mandate ids linked to mandate category ids
        :rparam: sta_mandate_ids
        :rtype: list of ids
        """
        mandate_categories = self.read(cr, uid, ids, ['sta_mandate_ids'], context=context)
        res_ids = []
        for mandate_category in mandate_categories:
            res_ids += mandate_category['sta_mandate_ids']
        return list(set(res_ids))

    _columns = {
        'name': fields.char('Name', size=128, translate=True, select=True, required=True, track_visibility='onchange'),
        'type': fields.selection(MANDATE_CATEGORY_AVAILABLE_TYPES, 'Status', readonly=True),
        'exclusive_category_m2m_ids': fields.many2many('mandate.category', 'mandate_category_mandate_category_rel', 'id', 'exclu_id',
                                                      'Exclusive Category'),
        'sta_assembly_category_id': fields.many2one('sta.assembly.category', string='State Assembly Category', track_visibility='onchange'),
        'ext_assembly_category_id': fields.many2one('ext.assembly.category', string='External Assembly Category', track_visibility='onchange'),
        'int_assembly_category_id': fields.many2one('int.assembly.category', string='Internal Assembly Category', track_visibility='onchange'),
        'int_power_level_id': fields.many2one('int.power.level', string='Internal Power Level',
                                                 required=True, track_visibility='onchange'),
        'sta_candidature_ids': fields.one2many('sta.candidature', 'mandate_category_id', 'State Candidatures'),
        'sta_mandate_ids': fields.one2many('sta.mandate', 'mandate_category_id', 'State Mandates'),
        'is_submission_mandate': fields.boolean('Submission to a mandate declaration'),
        'is_submission_assets': fields.boolean('Submission to an assets declaration'),
    }

    _order = 'name'

    def _check_unique_name(self, cr, uid, ids, context=None):

        for category in self.browse(cr, uid, ids, context=context):
            if len(self.search(cr, uid, [('id', '!=', category.id), ('name', '=', category.name)])) > 0:
                return False
        return True

    _constraints = [
        (_check_unique_name, _('Name must be unique'),
          ['name'])
    ]


class selection_committee(orm.Model):
    _name = 'selection.committee'
    _description = 'Selection Committee'
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
        'state': fields.selection(SELECTION_COMMITTEE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',),
        'committee_type': fields.selection(SELECTION_COMMITTEE_AVAILABLE_TYPES, 'Type', required=True, track_visibility='onchange',),
        'decision_date': fields.date('Decision Date', track_visibility='onchange'),
        'mandate_start_date': fields.date('Start date of mandate', required=True, track_visibility='onchange'),
        'mandate_deadline_date': fields.date('Deadline date of mandate', required=True, track_visibility='onchange'),
        'meeting_date': fields.date('Meeting date', track_visibility='onchange'),
        'name': fields.char('Name', size=128, translate=True, select=True, required=True, track_visibility='onchange'),
        'is_virtual': fields.boolean('Is virtual'),
        'partner_ids': fields.many2many('res.partner', 'selection_committee_res_partner_rel', 'id', 'member_id',
                                                      'Members', domain=[('is_company', '=', False)]),
        'sta_assembly_id': fields.many2one('sta.assembly', string='State Assembly', track_visibility='onchange'),
        'int_assembly_id': fields.many2one('int.assembly', string='Internal Assembly', track_visibility='onchange'),
        'ext_assembly_id': fields.many2one('ext.assembly', string='External Assembly', track_visibility='onchange'),
        'designation_int_assembly_id': fields.many2one('int.assembly', string='Internal Assembly (Designation)',
                                                 required=True, track_visibility='onchange', domain=[('is_designation_assembly', '=', True)]),
        'sta_candidature_ids': fields.one2many('sta.candidature', 'selection_committee_id', 'State Candidatures',
                                               domain=[('state', 'not in', ['draft'])]),
        'sta_candidature_inactive_ids': fields.one2many('sta.candidature', 'selection_committee_id', 'State Candidatures',
                                               domain=[('active', '=', False)]),
        'mandate_category_id': fields.many2one('mandate.category', string='Mandate Category',
                                                 required=True, track_visibility='onchange'),
        'electoral_district_id': fields.many2one('electoral.district', string='Electoral District', track_visibility='onchange'),
        'legislature_id': fields.many2one('legislature', string='Legislature', track_visibility='onchange'),
        'designation_int_power_level_id': fields.related('sta_assembly_id', 'designation_int_power_level_id', string='Designation Power Level',
                                          type='many2one', relation="int.power.level",
                                          store=True),
        'note': fields.text('Notes', track_visibility='onchange'),
        'sta_assembly_category_id': fields.related('mandate_category_id', 'sta_assembly_category_id', string='State assembly category',
                                          type='many2one', relation="sta.assembly.category",
                                          store=False),
        'int_assembly_category_id': fields.related('mandate_category_id', 'int_assembly_category_id', string='Internal assembly category',
                                          type='many2one', relation="int.assembly.category",
                                          store=False),
        'ext_assembly_category_id': fields.related('mandate_category_id', 'ext_assembly_category_id', string='External assembly category',
                                          type='many2one', relation="ext.assembly.category",
                                          store=False),
        'auto_mandate': fields.boolean("Create mandate after election")
    }

    _defaults = {
        'state': SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
        'is_virtual': False,
        'auto_mandate': False,
    }

# orm methods
    def name_get(self, cr, uid, ids, context=None):
        if not context:
            context = self.pool.get('res.users').context_get(cr, uid)

        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []

        for committee in self.browse(cr, uid, ids, context=context):
            if committee.committee_type == 'state':
                display_name = u'{name} {electoral_district} ({legislature_date})'.format(name=committee.name,
                                                                                          electoral_district=committee.electoral_district_id.name or committee.sta_assembly_id.name,
                                                                                          legislature_date=self.pool.get('res.lang').format_date(cr, uid, committee.legislature_id.start_date, context) or False,)
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

    def copy_data(self, cr, uid, id, default=None, context=None):
        default = default or {}

        default.update({
            'active': True,
            'state': SELECTION_COMMITTEE_AVAILABLE_STATES[0][0],
            'sta_candidature_ids': [],
            'sta_candidature_inactive_ids': [],
            'note': False,
            'decision_date': False,
            'meeting_date': False,
        })
        res = super(selection_committee, self).copy_data(cr, uid, id, default=default, context=context)

        data = self.onchange_sta_assembly_id(cr, uid, id, res.get('sta_assembly_id'), context=context)
        legislature_id = data['value']['legislature_id']
        legislature_data = self.onchange_legislature_id(cr, uid, id, legislature_id, context=context)

        res.update({
            'name': _('%s (copy)') % res.get('name'),
            'legislature_id': legislature_id,
            'mandate_start_date': legislature_data['value']['mandate_start_date'],
            'mandate_deadline_date': legislature_data['value']['mandate_deadline_date'],
        })
        return res

# view methods: onchange, button
    def action_copy(self, cr, uid, ids, context=None):
        """
        ==========================
        action_copy
        ==========================
        Duplicate committee and keep rejected state candidatures
        :rparam: True
        :rtype: boolean
        """
        copied_committee_id = ids[0]
        candidature_pool = self.pool.get('sta.candidature')
        rejected_candidature_ids = candidature_pool.search(cr, uid, [('selection_committee_id', '=', copied_committee_id),
                                                                                     ('state', '=', 'rejected')])
        new_committee_id = self.copy(cr, uid, copied_committee_id, None, context)
        if rejected_candidature_ids:
            candidature_pool.write(cr, uid, rejected_candidature_ids, {'selection_committee_id': new_committee_id})
            candidature_pool.signal_button_declare(cr, uid, rejected_candidature_ids)

        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_mandate', 'selection_committee_form_view')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': _('Selection Committee'),
            'res_model': 'selection.committee',
            'res_id': new_committee_id,
            'view_type': 'form',
            'view_mode': 'form',
            'view_id': view_id,
            'target': 'current',
            'nodestroy': True,
        }

    def button_accept_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_accept_candidatures
        ==========================
        This method calls the candidature workflow for each candidature_id in order to update their state
        :rparam: True
        :rtype: boolean
        :raise: Error if all candidatures are not in suggested state
        """
        for committee in self.browse(cr, uid, ids, context=context):
            if committee.committee_type == 'state':
                if committee.sta_candidature_ids:
                    self.pool.get('sta.candidature').signal_action_accept(cr, uid, self._get_suggested_sta_candidatures(committee.sta_candidature_ids))
        self.action_invalidate(cr, uid, ids, context, {'state': 'done'})
        return True

    def button_reject_candidatures(self, cr, uid, ids, context=None):
        """
        ==========================
        button_reject_candidatures
        ==========================
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
                                power_level_id=self.pool.get('ir.model.data').get_object_reference(cr, uid, 'ficep_structure', 'int_power_level_01')[1])
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

    def onchange_electoral_district_id(self, cr, uid, ids, electoral_district_id, context=None):
        res = {}
        res['value'] = dict(sta_assembly_id=False,
                            sta_assembly_category_id=False,
                            designation_int_assembly_id=False)
        if electoral_district_id:
            district_data = self.pool.get('electoral.district').read(cr, uid, electoral_district_id, ['assembly_id', 'designation_int_assembly_id'])
            res['value'] = dict(sta_assembly_id=district_data['assembly_id'] or False,
                                designation_int_assembly_id=district_data['designation_int_assembly_id'] or False)
        return res

    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        res = {}
        res['value'] = dict(int_assembly_category_id=False,
                                ext_assembly_category_id=False,
                                )
        if mandate_category_id:
            mandate_category = self.pool.get('mandate.category').browse(cr, uid, mandate_category_id, context)
            res['value'] = dict(int_assembly_category_id=mandate_category.int_assembly_category_id.id or False,
                                ext_assembly_category_id=mandate_category.ext_assembly_category_id.id or False,
                                )
        return res

    def onchange_legislature_id(self, cr, uid, ids, legislature_id, context=None):
        res = {}
        res['value'] = dict(mandate_start_date=False,
                                mandate_deadline_date=False)
        if legislature_id:
            legislature_data = self.pool.get('legislature').read(cr, uid, legislature_id, ['start_date', 'deadline_date'])
            res['value'] = dict(mandate_start_date=legislature_data['start_date'],
                                mandate_deadline_date=legislature_data['deadline_date'])
        return res

    def onchange_sta_assembly_id(self, cr, uid, ids, sta_assembly_id, context=None):
        res = {}
        res['value'] = dict(sta_assembly_category_id=False,
                            legislature_id=False,
                            designation_int_power_level_id=False,
                            mandate_category_id=False)
        if sta_assembly_id:
            sta_assembly = self.pool.get('sta.assembly').browse(cr, uid, sta_assembly_id)
            legislature_ids = self.pool.get('legislature').search(cr, uid, [('power_level_id', '=', sta_assembly.assembly_category_id.power_level_id.id),
                                                                            ('start_date', '>', fields.datetime.now())])
            legislature_id = False
            if legislature_ids:
                legislature_id = legislature_ids[0]

            mandate_category_ids = self.pool.get('mandate.category').search(cr, uid, [('sta_assembly_category_id', '=', sta_assembly.assembly_category_id.id)])
            mandate_category_id = False
            if mandate_category_ids:
                mandate_category_id = mandate_category_ids[0]

            res['value'] = dict(sta_assembly_category_id=sta_assembly.assembly_category_id.id or False,
                                legislature_id=legislature_id,
                                designation_int_power_level_id=sta_assembly.designation_int_power_level_id.id,
                                mandate_category_id=mandate_category_id)
        return res
