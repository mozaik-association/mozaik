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


class res_partner(orm.Model):

    _name = 'res.partner'
    _inherit = ['res.partner']

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

    @api.multi
    def _get_assembly_ids(self):
        """
        return the assemblies' ids of the current partner
        """
        self.ensure_one()
        assembly_model = 'ext.assembly'
        if self.is_assembly:
            field = 'partner_id'
        else:
            field = 'ref_partner_id'
        domain = [(field, '=', self.id)]

        assembly_obj = self.env[assembly_model]
        assemblies = assembly_obj.search(domain)
        assembly_ids = [assembly.id for assembly in assemblies]

        return assembly_ids

    @api.multi
    def _get_mandate_ids(self):
        """
        return list of mandates linked to the assemblies of the
        current partner
        """
        self.ensure_one()
        mandate_model = 'ext.mandate'
        prefix = 'ext'
        mandate_obj = self.env[mandate_model]

        assembly_ids = self._get_assembly_ids()
        domain = [('%s_assembly_id' % prefix, 'in', assembly_ids)]
        mandates = mandate_obj.search(domain)
        mandate_ids = [mandate.id for mandate in mandates]

        return mandate_ids

    @api.one
    def _compute_mandate_count(self):
        """
        count the number of mandates linked to the assemblies of the
        current partner
        """
        self.ext_mandate_count = len(self._get_mandate_ids())

    @api.one
    def _compute_assembly_count(self):
        """
        count the number of assemblies linked to the current partner
        """
        self.ext_assembly_count = len(self._get_assembly_ids())

    _columns = {
        'sta_mandate_ids': fields.one2many(
            'sta.mandate', 'partner_id', string='State Mandates',
            domain=[('active', '=', True)], context={'force_recompute': True}),
        'sta_mandate_inactive_ids': fields.one2many(
            'sta.mandate', 'partner_id', string='State Mandates',
            domain=[('active', '=', False)]),
        'sta_candidature_ids': fields.one2many(
            'sta.candidature', 'partner_id', string='State Candidatures',
            domain=[('active', '=', True)]),
        'sta_candidature_inactive_ids': fields.one2many(
            'sta.candidature', 'partner_id', string='State Candidatures',
            domain=[('active', '=', False)]),
        'int_mandate_ids': fields.one2many(
            'int.mandate', 'partner_id', string='Internal Mandates',
            domain=[('active', '=', True)], context={'force_recompute': True}),
        'int_mandate_inactive_ids': fields.one2many(
            'int.mandate', 'partner_id', string='Internal Mandates',
            domain=[('active', '=', False)]),
        'int_candidature_ids': fields.one2many(
            'int.candidature', 'partner_id', string='Internal Candidatures',
            domain=[('active', '=', True)]),
        'int_candidature_inactive_ids': fields.one2many(
            'int.candidature', 'partner_id', string='Internal Candidatures',
            domain=[('active', '=', False)]),
        'ext_mandate_ids': fields.one2many(
            'ext.mandate', 'partner_id', string='External Mandates',
            domain=[('active', '=', True)], context={'force_recompute': True}),
        'ext_mandate_inactive_ids': fields.one2many(
            'ext.mandate', 'partner_id', string='External Mandates',
            domain=[('active', '=', False)]),
        'ext_candidature_ids': fields.one2many(
            'ext.candidature', 'partner_id', string='External Candidatures',
            domain=[('active', '=', True)]),
        'ext_candidature_inactive_ids': fields.one2many(
            'ext.candidature', 'partner_id', string='External Candidatures',
            domain=[('active', '=', False)]),
    }

    ext_mandate_count = new_fields.Integer(
        string='External Mandates', compute='_compute_mandate_count')
    ext_assembly_count = new_fields.Integer(
        string='External Assemblies', compute='_compute_assembly_count')

# orm methods

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        """
        default = default or {}
        default.update({
            'sta_mandate_ids': [],
            'sta_mandate_inactive_ids': [],
            'int_mandate_ids': [],
            'int_mandate_inactive_ids': [],
            'ext_mandate_ids': [],
            'ext_mandate_inactive_ids': [],
            'sta_candidature_ids': [],
            'sta_candidature_inactive_ids': [],
            'int_candidature_ids': [],
            'int_candidature_inactive_ids': [],
            'ext_candidature_ids': [],
            'ext_candidature_inactive_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default,
                                                 context=context)
        return res

    @api.multi
    def get_mandate_action(self):
        """
        return an action for an ext.mandate contains into the domain a
        specific tuples to get concerned mandates
        """
        self.ensure_one()
        module = 'mozaik_mandate'
        action_name = 'ext_mandate_action'
        res_ids = self._get_mandate_ids()
        domain = [('id', 'in', res_ids)]

        # get model's action to update its domain
        action = self.env['ir.actions.act_window'].for_xml_id(
            module, action_name)
        action['domain'] = domain
        return action
