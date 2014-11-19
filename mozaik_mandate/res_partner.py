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


class res_partner(orm.Model):

    _name = 'res.partner'
    _inherit = ['res.partner']

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

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
