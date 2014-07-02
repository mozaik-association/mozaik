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


class res_partner(orm.Model):

    _inherit = 'res.partner'

# view methods: onchange, button

    def button_modification_request(self, cr, uid, ids, context=None):
        """
        ====================
        modification_request
        ====================
        Create a `membership.request` object with the datas of the current partner.
        Launch it into the another form view
        """
        partners = self.browse(cr, uid, ids, context=context)
        partner = partners and partners[0]
        if not partner:
            raise orm.except_orm(_('Error'), _('Modification request must be launch with a valid partner id'))
        postal_coordinate_id = partner.postal_coordinate_id or False
        mobile_coordinate_id = partner.mobile_coordinate_id or False
        fix_coordinate_id = partner.fix_coordinate_id or False
        email_coordinate_id = partner.email_coordinate_id or False
        int_instance_id = partner.int_instance_id or False
        birth_date = partner.birth_date
        day = False
        month = False
        year = False
        if partner.birth_date:
            datas = partner.birth_date.split('-')
            day = datas[2]
            month = datas[1]
            year = datas[0]

        values = {
            'lastname': partner.lastname,
            'firstname': partner.firstname,
            'gender': partner.gender,
            'birth_date': birth_date,
            'day': day,
            'month': month,
            'year': year,
            'is_update': True,

            #country_id is mandatory
            'country_id': postal_coordinate_id and postal_coordinate_id.address_id.country_id.id,
            'address_local_street_id': postal_coordinate_id and postal_coordinate_id.address_id.address_local_street_id.id,
            'street_man': postal_coordinate_id and postal_coordinate_id.address_id.street_man,
            'street2': postal_coordinate_id and postal_coordinate_id.address_id.street2,
            'address_local_zip_id': postal_coordinate_id and postal_coordinate_id.address_id.address_local_zip_id.id,
            'zip_man': postal_coordinate_id and postal_coordinate_id.address_id.zip_man,
            'town_man': postal_coordinate_id and postal_coordinate_id.address_id.town_man,
            'box': postal_coordinate_id and postal_coordinate_id.address_id.box,
            'number': postal_coordinate_id and postal_coordinate_id.address_id.number,

            'mobile': mobile_coordinate_id and mobile_coordinate_id.phone_id.name,
            'phone': fix_coordinate_id and fix_coordinate_id.phone_id.name,
            'mobile_id': mobile_coordinate_id and mobile_coordinate_id.phone_id.id,
            'phone_id': fix_coordinate_id and fix_coordinate_id.phone_id.id,

            'email': email_coordinate_id and email_coordinate_id.email,

            'partner_id': partner.id,
            'address_id': postal_coordinate_id and postal_coordinate_id.address_id.id,
            'int_instance_id': int_instance_id and int_instance_id.id,

            'interests_m2m_ids': [[6, False, partner.interests_m2m_ids and [interest.id for interest in partner.interests_m2m_ids] or []]],
            'competencies_m2m_ids': [[6, False, partner.competencies_m2m_ids and [competence.id for competence in partner.competencies_m2m_ids] or []]],
        }
        membership_request_obj = self.pool['membership.request']
        membership_request_id = membership_request_obj.create(cr, uid, values, context=context)
        return membership_request_obj.display_object_in_form_view(cr, uid, membership_request_id, context=None)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
