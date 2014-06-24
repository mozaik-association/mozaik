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
from datetime import date
from openerp.osv import orm, fields

from openerp.addons.ficep_person.res_partner \
    import AVAILABLE_TONGUES, AVAILABLE_GENDERS, AVAILABLE_CIVIL_STATUS

MEMBERSHIP_AVAILABLE_STATES = [
    ('draft', 'Unconfirmed'),
    ('confirm', 'Confirmed'),
    ('cancel', 'Cancelled'),
]
membership_available_states = dict(MEMBERSHIP_AVAILABLE_STATES)

MEMBERSHIP_REQUEST_TYPE = [
    ('m', 'Member'),
    ('s', 'Supporter'),
]
membership_request_type = dict(MEMBERSHIP_REQUEST_TYPE)


class membership_request(orm.Model):

    _name = 'membership.request'
    _inherit = ['abstract.ficep.model']
    _description = 'Membership Request'

    _columns = {
        'lastname': fields.char('Lastname', required=True, track_visibility='onchange'),
        'firstname': fields.char('Firstname', required=True, track_visibility='onchange'),
        'state': fields.selection(MEMBERSHIP_AVAILABLE_STATES, 'Status', required=True, track_visibility='onchange'),
        'status': fields.selection(MEMBERSHIP_REQUEST_TYPE, 'Type', required=True, track_visibility='onchange'),

        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender', select=True, track_visibility='onchange'),
        'email': fields.char('Email', track_visibility='onchange'),
        'phone': fields.char('Phone', track_visibility='onchange'),
        'mobile': fields.char('Mobile', track_visibility='onchange'),
        'day': fields.integer('Day'),
        'month': fields.integer('Month'),
        'year': fields.integer('Year'),
        'birth_date': fields.date('Birthdate', track_visibility='onchange'),

        'country': fields.char('Country'),
        'street': fields.char('Street'),
        'zip_code': fields.char('Town'),

        'interests': fields.char(string='Interests'),

        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='restrict'),
        'int_instance_id': fields.many2one('int.instance', 'Internal Instance', ondelete='restrict'),
        'address_local_zip_id': fields.many2one('address.local.zip', string='City', track_visibility='onchange'),
        'address_local_street_id': fields.many2one('address.local.street', string='Street', track_visibility='onchange'),

        'mobile_coordinate_id': fields.many2one('res.partner', 'Mobile Coordinate', ondelete='restrict'),
        'mobile_id': fields.many2one('phone.phone', 'Mobile', ondelete='restrict'),
        'phone_coordinate_id': fields.many2one('phone.coordinate', 'Phone Coordinate', ondelete='restrict'),
        'phone_id': fields.many2one('phone.phone', 'Phone', ondelete='restrict'),
        'email_coordinate_id': fields.many2one('email.coordinate', 'Email Coordinate', ondelete='restrict'),
    }

    _unicity_keys = 'N/A'

    _defaults = {
        'state': 'draft',
    }

    # public method

    def pre_process(self, cr, uid, vals, context=None):
        """
        ===========
        pre_process
        ===========
        * Try to create a birth_date if all the components are there. (day/month/year)
        * Try to normalize email/phone/mobile
        * Next step is to find partner by different way:
        ** birth_date + email
        ** birth_date + lastname + firstname
        ** email + firstname + lastname
        ** email
        ** firstname + lastname
        * Case of partner found: search email coordinate and phone coordinate for this partner
        * Try to find street_id and zip_id

        :rparam vals: dictionary used to create ``membership_request``
        """
        if context is None:
            context = {}

        birth_date = False
        mobile_coordinate_ids = False
        mobile_id = False
        mobile_ids = False
        phone_coordinate_ids = False
        phone_id = False
        phone_ids = False
        email_coordinate_ids = False

        firstname = vals.get('firstname', False)
        lastname = vals.get('lastname', False)
        day = vals.get('day', False)
        month = vals.get('month', False)
        year = vals.get('year', False)
        email = vals.get('email', False)
        mobile = vals.get('mobile', False)
        phone = vals.get('phone', False)
        zip_code = vals.get('zip_code', False)
        town = vals.get('town', False)
        street = vals.get('street', False)
        gender = vals.get('gender', False)
        status = vals.get('status', False)
        interest = vals.get('interest', False)

        if day and month and year:
            birth_date = date(year, month, day)
        if email:
            email_obj = self.pool['email.coordinate']
            if email_obj._check_email_format(cr, uid, email, context=context) != None:
                email = email_obj.format_email(cr, uid, email, context=context)
        if mobile or phone:
            ctx = context.copy()
            ctx.update({'install_mode': True})
            phone_obj = self.pool['phone.phone']

            if mobile:
                mobile = phone_obj._check_and_format_number(cr, uid, mobile, context=ctx)
                # try to find this number into phone.phone records with type `mobile`
                mobile_ids = phone_obj.search(cr, uid, [('name', '=', mobile), ('type', '=', 'mobile')])
            if phone:
                phone = self.pool['phone.phone']._check_and_format_number(cr, uid, phone, context=ctx)
                # try to find this number into phone.phone records with type `fix`
                phone_ids = phone_obj.search(cr, uid, [('name', '=', phone), ('type', '=', 'fix')])

        partner_obj = self.pool['virtual.custom.partner']
        partner_domains = []
        if birth_date and email:
            partner_domains.append("[('birth_date', '=', '%s'),('email', '=', '%s')]" % (birth_date, email))
        if birth_date and email and firstname and lastname:
            partner_domains.append("[('birth_date', '=', '%s'),('email', '=', '%s'),('firstname', 'ilike', '%s'), ('lastname', 'ilike', '%s')]"\
                       % (birth_date, email, firstname, lastname))
        if email:
            partner_domains.append("[('email', '=', '%s')]" % (email))
        if firstname and lastname:
            partner_domains.append("[('firstname', 'ilike', '%s'),('lastname', 'ilike', '%s')]" % (firstname, lastname))

        partner_id = self.persist_search(cr, uid, partner_obj, partner_domains, context=context)

        if partner_id:
            # because this is not a real partner but a virtual partner
            partner_id = partner_obj.read(cr, uid, [partner_id], ['partner_id'])[0]
            partner_id = partner_id['partner_id'][0]
            if mobile_ids or mobile_ids:
                phone_coo = self.pool['phone.coordinate']
                # then try to match other datas of the partner with the input datas
                if mobile_ids:
                    mobile_id = mobile_ids[0]
                    # try to find a coordinate with partner_id and mobile_id
                    mobile_coordinate_ids = phone_coo.search(cr, uid, [('partner_id', '=', partner_id), ('phone_id', '=', mobile_id)])
                if phone_ids:
                    phone_id = phone_ids[0]
                    # try to find a coordinate with partner_id and fix_id
                    phone_coordinate_ids = phone_coo.search(cr, uid, [('partner_id', '=', partner_id), ('phone_id', '=', phone_id)])
            if email:
                email_coordinate_ids = self.pool['email.coordinate'].search(cr, uid, [('partner_id', '=', partner_id), ('email', '=', email)], context=context)

        # Find local zip code
        address_local_zip_obj = self.pool['address.local.zip']
        address_local_zip_domains = ["[('local_zip', '=', '%s')]" % zip_code,
                                     "[('local_zip', '=', '%s'),('town', '=', '%s')]" % (zip_code, town)]
        address_local_zip_id = self.persist_search(cr, uid, address_local_zip_obj, address_local_zip_domains, context=context)

        # find local street
        address_local_street_obj = self.pool['address.local.street']
        address_local_street_domains = ["[('local_street', '=', '%s')]" % street]
        if address_local_zip_id:
            address_local_street_domains.append("[('local_street','=', '%s'),('local_zip', '=', '%s')]" % (street, town))

        address_local_street_id = self.persist_search(cr, uid, address_local_street_obj, address_local_street_domains, context=context)

        #update vals dictionary because some inputs may have changed (and new values too)
        vals.update({
            'partner_id': partner_id,
            'lastname': lastname,
            'firstname': firstname,
            'gender': gender,
            'birth_date': birth_date,
            'day': day,
            'month': month,
            'year': year,

            'status': status,
            'street': street,
            'zip_code': zip_code,
            'town': town,

            'mobile': mobile,
            'phone': phone,
            'email': email,

            'mobile_coordinate_id': mobile_coordinate_ids if not mobile_coordinate_ids else mobile_coordinate_ids[0],
            'mobile_id': mobile_id,
            'phone_coordinate_id': phone_coordinate_ids if not phone_coordinate_ids else phone_coordinate_ids[0],
            'phone_id': phone_id,
            'email_coordinate_id': email_coordinate_ids if not email_coordinate_ids else email_coordinate_ids[0],
            'address_local_zip_id': address_local_zip_id,
            'address_local_street_id': address_local_street_id,

            'interest': interest,
        })

        return vals

    def persist_search(self, cr, uid, model_obj, domains, context=None):
        """
        ==============
        persist_search
        ==============
        This method will make a search with a list of domain and return result only
        if it is a single result
        :type model_obj: model object into odoo (ex: res.partner)
        :param model_obj: used to make the research
        :type domains: []
        :param domains: contains a list of domains
        :rparam: result of the search
        """
        def rec_search(loop_counter):
            if loop_counter >= len(domains):
                return False
            else:
                model_ids = model_obj.search(cr, uid, eval(domains[loop_counter]), context=context)
                if len(model_ids) == 1:
                    return model_ids[0]
                else:
                    return rec_search(loop_counter + 1)

        return rec_search(0)

    def confirm_request(self, cr, uid, ids, context=None):
        pass

    def cancel_request(self, cr, uid, ids, context=None):
        pass

# orm methods

    def create(self, cr, uid, vals, context=None):
        """
        ======
        create
        ======
        Call ``pre-process`` function to prepare input values.
        """
        self.pre_process(cr, uid, vals, context=context)
        return super(membership_request, self).create(cr, uid, vals, context=context)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
