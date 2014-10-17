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

    _inherit = 'res.partner'

    _allowed_inactive_link_models = ['res.partner']
    _inactive_cascade = True

# data model

    _columns = {
        # relation fields
        'partner_is_subject_relation_ids': fields.one2many('partner.relation', 'subject_partner_id', string='Subject Relations', domain=[('active', '=', True)]),
        'partner_is_object_relation_ids': fields.one2many('partner.relation', 'object_partner_id', string='Object Relations', domain=[('active', '=', True)]),

        'partner_is_subject_relation_inactive_ids': fields.one2many('partner.relation', 'subject_partner_id', string='Subject Relations', domain=[('active', '=', False)]),
        'partner_is_object_relation_inactive_ids': fields.one2many('partner.relation', 'object_partner_id', string='Object Relations', domain=[('active', '=', False)]),
    }

    def copy_data(self, cr, uid, ids, default=None, context=None):
        """
        Do not copy o2m fields.
        Reset some fields to their initial values.
        """
        default = default or {}
        default.update({
            'partner_is_subject_relation_ids': [],
            'partner_is_object_relation_ids': [],
            'partner_is_subject_relation_inactive_ids': [],
            'partner_is_object_relation_inactive_ids': [],
        })
        res = super(res_partner, self).copy_data(cr, uid, ids, default=default, context=context)
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
