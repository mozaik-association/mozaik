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
from openerp.tools import SUPERUSER_ID

from openerp.addons.ficep_person.res_partner \
    import AVAILABLE_TONGUES, AVAILABLE_GENDERS, AVAILABLE_CIVIL_STATUS

MEMBERSHIP_AVAILABLE_STATES = [
    ('draft', 'Unconfirmed'),
    ('confirm', 'Confirmed'),
    ('cancel', 'Cancelled'),
]
membership_available_states = dict(MEMBERSHIP_AVAILABLE_STATES)

MEMBERSHIP_REQUEST_TYPE = [
    ('member', 'Member'),
    ('supporter', 'Supporter'),
]
membership_request_type = dict(MEMBERSHIP_REQUEST_TYPE)


class membership_request(orm.Model):

    _name = 'membership.request'
    _inherit = ['abstract.ficep.model']

    _columns = {
        'lastname': fields.char('Lastname', required=True, track_visibility='onchange'),
        'firstname': fields.char('Firstname', required=True, track_visibility='onchange'),
        'state': fields.selection(MEMBERSHIP_AVAILABLE_STATES, 'Status', required=True, track_visibility='onchange'),

        'tongue': fields.selection(AVAILABLE_TONGUES, 'Tongue', select=True, track_visibility='onchange'),
        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender', select=True, track_visibility='onchange'),
        'civil_status': fields.selection(AVAILABLE_CIVIL_STATUS, 'Civil Status', track_visibility='onchange'),
        'email': fields.char('Email', track_visibility='onchange'),
        'phone': fields.char('Phone', track_visibility='onchange'),
        'fax': fields.char('Fax', track_visibility='onchange'),
        'mobile': fields.char('Mobile', track_visibility='onchange'),
        'birth_date': fields.char('Birthdate', track_visibility='onchange'),

        'country': fields.char('Country'),
        'street': fields.char('Street'),
        'zip': fields.char('Zip'),
        'note': fields.char('Note', track_visibility='onchange'),

        'competencies': fields.char(string='Competencies'),
        'interests': fields.char(string='Interests'),
        'tags': fields.char(string='Tags'),

        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='restrict'),
    }

    defaults = {
        'state': 'draft',
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
