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
from .mandate import mandate_category

STA_CANDIDATURE_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('declared', 'Declared'),
    ('suggested', 'Suggested'),
    ('designated', 'Designated'),
    ('rejected', 'Rejected'),
    ('elected', 'Elected'),
    ('non-elected', 'Non-Elected'),
]

sta_candidature_available_states = dict(STA_CANDIDATURE_AVAILABLE_STATES)


class res_partner(orm.Model):
    _name = 'res.partner'
    _inherit = ['res.partner']

    def get_linked_sta_candidature_ids(self, cr, uid, ids, context=None):
        """
        ============================
        get_linked_sta_candidature_ids
        ============================
        Return State Candidature ids linked to partner ids
        :rparam: sta_candidature_ids
        :rtype: list of ids
        """
        partners = self.read(cr, uid, ids, ['sta_candidature_ids'], context=context)
        res_ids = []
        for partner in partners:
            res_ids += partner['sta_candidature_ids']
        return list(set(res_ids))

    _columns = {
        'sta_candidature_ids': fields.one2many('sta.candidature', 'partner_id', 'State Candidatures'),
    }


class sta_candidature(orm.Model):

    _name = 'sta.candidature'
    _description = "State Candidature"
    _inherit = ['abstract.mandate']

    def _compute_name(self, cr, uid, ids, fname, arg, context=None):
        return super(sta_candidature, self)._compute_name(cr, uid, ids, fname, arg, context=context)

    _name_store_triggers = {
        'sta.candidature': (lambda self, cr, uid, ids, context=None: ids,
                         ['partner_name', 'partner_id', 'mandate_category_id', ], 10),
        'mandate.category': (mandate_category.get_linked_sta_candidature_ids, ['name'], 20),
        'res.partner': (res_partner.get_linked_sta_candidature_ids, ['name'], 20),
    }

    _columns = {
        'name': fields.function(_compute_name, string="Name",
                                 type="char", store=_name_store_triggers,
                                 select=True),
        'state': fields.selection(STA_CANDIDATURE_AVAILABLE_STATES, 'Status', readonly=True, track_visibility='onchange',
            ),
        'electoral_district_id': fields.many2one('electoral.district', string='Electoral District',
                                                 required=True, track_visibility='onchange'),
        'legislature_id': fields.many2one('legislature', string='Legislature',
                                                 required=True, track_visibility='onchange'),
        'selection_committee_id': fields.many2one('selection.committee', string='Selection Committee',
                                                 required=True, track_visibility='onchange'),
        'sta_assembly_id': fields.related('electoral_district_id', 'assembly_id', string='State Assembly',
                                          type='many2one', relation="sta.assembly",
                                          store=False),
        'sta_assembly_category_id': fields.related('mandate_category_id', 'sta_assembly_category_id', string='State Assembly Category',
                                          type='many2one', relation="sta.assembly.category",
                                          store=False),
        'sta_power_level_id': fields.related('sta_assembly_category_id', 'power_level_id', string='State Power Level',
                                          type='many2one', relation="sta.power.level",
                                          store=False),
        'is_substitute': fields.boolean('Substitute ?')
        }

    def _check_partner(self, cr, uid, ids, for_unlink=False, context=None):
        """
        =================
        _check_partner
        =================
        Check if partner doesn't have several candidatures in the same category
        :rparam: True if it is the case
                 False otherwise
        :rtype: boolean
        """
        candidatures = self.browse(cr, uid, ids)
        for candidature in candidatures:
            if len(self.search(cr, uid, [('partner_id', '=', candidature.partner_id.id), ('id', '!=', candidature.id)], context=context)) > 0:
                return False

        return True

    _constraints = [
        (_check_partner, _("A candidature already exists for this partner in this category"), ['partner_id'])
    ]

    _defaults = {
        'state': 'draft',
    }

    # view methods: onchange, button
    def onchange_mandate_category_id(self, cr, uid, ids, mandate_category_id, context=None):
        res = {}
        sta_category_id = False
        if mandate_category_id:
            sta_category_id_val = self.pool.get('mandate.category').read(cr, uid, mandate_category_id, ['sta_assembly_category_id'])['sta_assembly_category_id']
            if sta_category_id_val:
                sta_category_id = sta_category_id_val[0]

        res['value'] = dict(electoral_distric_id=False,
                            sta_assembly_category_id=sta_category_id)
        return res

    def onchange_electoral_district_id(self, cr, uid, ids, electoral_district_id, context=None):
        res = {}
        sta_assembly_id = False
        if electoral_district_id:
            sta_assembly_id = self.pool.get('electoral.district').read(cr, uid, electoral_district_id, ['assembly_id'])['assembly_id']
        res['value'] = dict(sta_assembly_id=sta_assembly_id)
        return res

    def onchange_sta_assembly_category_id(self, cr, uid, ids, sta_assembly_category_id, context=None):
        res = {}
        sta_power_level_id = False
        if sta_assembly_category_id:
            sta_power_level_id = self.pool.get('sta.assembly.category').read(cr, uid, sta_assembly_category_id, ['power_level_id'])['power_level_id']
        res['value'] = dict(sta_power_level_id=sta_power_level_id)
        return res

    def onchange_sta_power_level_id(self, cr, uid, ids, sta_power_level_id, context=None):
        res = {}
        legislature_id = False
        if sta_power_level_id:
            SQL = '''
                    SELECT id, max(create_date)
                    FROM legislature
                     WHERE power_level_id = %s
                     AND active = True
                    GROUP BY id LIMIT 1
                  '''
            cr.execute(SQL, (sta_power_level_id,))
            legislature_id = cr.fetchone()[0]
        res['value'] = dict(legislature_id=legislature_id)
        return res