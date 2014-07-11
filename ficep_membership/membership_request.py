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
from collections import OrderedDict

from openerp.tools import logging
from openerp.osv import orm, fields

from openerp.addons.ficep_address.address_address import COUNTRY_CODE
from openerp.addons.ficep_person.res_partner import AVAILABLE_GENDERS
from openerp.tools import SUPERUSER_ID

_logger = logging.getLogger(__name__)

MEMBERSHIP_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('confirm', 'Confirmed'),
    ('validate', 'Done'),
    ('cancel', 'Cancelled'),
]
membership_available_states = dict(MEMBERSHIP_AVAILABLE_STATES)

EMPTY_ADDRESS = '0#0#0#0#0#0#0#0'
MEMBERSHIP_REQUEST_TYPE = [
    ('m', 'Member'),
    ('s', 'Supporter'),
]
membership_request_type = dict(MEMBERSHIP_REQUEST_TYPE)


class membership_request(orm.Model):

    def _pop_related(self, cr, uid, vals, context=None):
        vals.pop('local_zip', None)
        vals.pop('country_code', None)

    _name = 'membership.request'
    _inherit = ['abstract.ficep.model']
    _description = 'Membership Request'

    _columns = {
        'lastname': fields.char('Lastname', required=True, track_visibility='onchange'),
        'firstname': fields.char('Firstname', track_visibility='onchange'),
        'state': fields.selection(MEMBERSHIP_AVAILABLE_STATES, 'Status', track_visibility='onchange'),
        'status': fields.selection(MEMBERSHIP_REQUEST_TYPE, 'Type', track_visibility='onchange'),

        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender', select=True, track_visibility='onchange'),
        'email': fields.char('Email', track_visibility='onchange'),
        'phone': fields.char('Phone', track_visibility='onchange'),
        'mobile': fields.char('Mobile', track_visibility='onchange'),
        'day': fields.integer('Day'),
        'month': fields.integer('Month'),
        'year': fields.integer('Year'),
        'birth_date': fields.date('Birthdate', track_visibility='onchange'),

        'is_update': fields.boolean('Is Update'),

        # address
        'country_id': fields.many2one('res.country', 'Country', select=True, track_visibility='onchange'),
        'country_code': fields.related('country_id', 'code', string='Country Code', type='char'),

        'address_local_zip_id': fields.many2one('address.local.zip', string='City', track_visibility='onchange'),
        'zip_man': fields.char(string='Zip', track_visibility='onchange'),

        'town_man': fields.char(string='Town', track_visibility='onchange'),

        'address_local_street_id': fields.many2one('address.local.street', string='Reference Street', track_visibility='onchange'),
        'street_man': fields.char(string='Street', track_visibility='onchange'),

        'street2': fields.char(string='Street2', track_visibility='onchange'),
        'sequence': fields.integer('Sequence'),

        'number': fields.char(string='Number', track_visibility='onchange'),
        'box': fields.char(string='Box', track_visibility='onchange'),

        'technical_name': fields.char(string='Technical Name'),

        'interests': fields.text(string='Interests'),
        'competencies': fields.text(string='Competencies'),

        'partner_id': fields.many2one('res.partner', 'Partner', ondelete='restrict'),
        'interests_m2m_ids': fields.many2many('thesaurus.term', 'membership_request_interests_rel',
                                              id1='membership_id', id2='thesaurus_term_id', string='Interests'),
        'competencies_m2m_ids': fields.many2many('thesaurus.term', 'membership_request_competence_rel',
                                              id1='membership_id', id2='thesaurus_term_id', string='Competencies'),
        'int_instance_id': fields.many2one('int.instance', 'Internal Instance', ondelete='restrict'),
        'address_local_zip_id': fields.many2one('address.local.zip', string='City', track_visibility='onchange'),
        # used for the domain on street
        'local_zip': fields.related('address_local_zip_id', 'local_zip', string='Local Zip', type='char'),
        'address_local_street_id': fields.many2one('address.local.street', string='Referenced Street', track_visibility='onchange'),
        'address_id': fields.many2one('address.address', string='Address', track_visibility='onchange'),

        'mobile_id': fields.many2one('phone.phone', 'Mobile', ondelete='restrict'),
        'phone_id': fields.many2one('phone.phone', 'Phone', ondelete='restrict'),

        'note': fields.text('Note'),
    }

    _unicity_keys = 'N/A'

    _defaults = {
        'country_id': lambda self, cr, ids, uid, c=None:
            self.pool.get('res.country')._country_default_get(cr, uid, COUNTRY_CODE),
        'country_code': COUNTRY_CODE,
        'is_update': False,
        'state': 'draft'
    }

# view methods: onchange, button

    def onchange_country_id(self, cr, uid, ids, address_local_street_id, address_local_zip_id, \
                                 number, box, town_man, street_man, zip_man, country_id, context=None):
        return {
            'value': {
                'country_code': self.pool.get('res.country').read(cr, uid, \
                                [country_id], ['code'], context=context)[0]['code']
                                if country_id else False,
                'address_local_zip_id': False,
                'technical_name': self.get_technical_name(cr, uid, address_local_street_id, address_local_zip_id, \
                                                          number, box, town_man, street_man, zip_man, country_id, context=context)
             }
        }

    def onchange_local_zip_id(self, cr, uid, ids, address_local_street_id, address_local_zip_id, \
                              number, box, town_man, street_man, zip_man, country_id, context=None):
        # local_zip used for domain
        local_zip = False
        if address_local_zip_id:
            local_zip = self.pool['address.local.zip'].read(cr, uid, [address_local_zip_id], ['local_zip'], context=context)
        if local_zip:
            local_zip = local_zip[0]['local_zip']
        return {
            'value': {
                'address_local_street_id': False,
                'technical_name': self.get_technical_name(cr, uid, address_local_street_id, address_local_zip_id, \
                                                          number, box, town_man, street_man, zip_man, country_id=country_id, context=context),
                'local_zip': local_zip,
             }
        }

    def onchange_other_address_componants(self, cr, uid, ids, address_local_street_id, address_local_zip_id, \
                                 number, box, town_man, street_man, zip_man, country_id, context=None):
        return {
            'value': {
                'technical_name': self.get_technical_name(cr, uid, address_local_street_id, address_local_zip_id, \
                                                          number, box, town_man, street_man, zip_man, country_id, context=context)
            }
        }

    def onchange_technical_name(self, cr, uid, ids, technical_name, context=None):
        address_ids = self.pool['address.address'].search(cr, uid, [('technical_name', '=', technical_name)], context=context)
        return {
            'value': {
                'address_id': address_ids and address_ids[0] or False
            }
        }

    def onchange_partner_component(self, cr, uid, ids, day, month, year, lastname, firstname, email, is_update, context=None):
        """
        ===================
        onchange_country_id
        ===================
        try to find a new partner_id depending of the
        birth_date, lastname, firstname, email
        """
        birth_date = self.get_birth_date(cr, uid, day, month, year, context=context)
        email = self.get_format_email(cr, uid, email, context=context)
        values = {
            'value': {
                'birth_date': '%s' % birth_date if birth_date else False,
                'email': email,
            }
        }
        if is_update:
            return values

        partner_id = self.get_partner_id(cr, uid, birth_date, firstname, lastname, email, context=context)
        values['value'].update({
            'partner_id': partner_id,
        })
        return values

    def onchange_partner_id(self, cr, uid, ids, partner_id, context=None):
        interests_ids = []
        competencies_ids = []
        if partner_id:
            partner = self.pool['res.partner'].browse(cr, uid, partner_id, context=context)
            interests_ids = partner.interests_m2m_ids and ([interest.id for interest in partner.interests_m2m_ids]) or False
            competencies_ids = partner.competencies_m2m_ids and ([competence.id for competence in partner.competencies_m2m_ids]) or False
            int_instance_id = partner.int_instance_id and partner.int_instance_id.id or False
        return {
            'value': {
                'int_instance_id': int_instance_id,
                'interests_m2m_ids': interests_ids and [[6, False, interests_ids]] or interests_ids,
                'competencies_m2m_ids': competencies_ids and [[6, False, competencies_ids]] or competencies_ids,
            }
        }

    def onchange_mobile(self, cr, uid, ids, mobile, context=None):
        mobile = self.get_format_phone_number(cr, uid, mobile, context=context)
        mobile_id = self.get_phone_id(cr, uid, mobile, 'mobile', context=context)
        return {
            'value': {
                'mobile_id': mobile_id,
                'mobile': mobile,
            }
        }

    def onchange_phone(self, cr, uid, ids, phone, context=None):
        phone = self.get_format_phone_number(cr, uid, phone, context=context)
        phone_id = self.get_phone_id(cr, uid, phone, 'fix', context=context)
        return {
            'value': {
                'phone_id': phone_id,
                'phone': phone,
            }
        }

    # public method

    def get_birth_date(self, cr, uid, day, month, year, context=None):
        """
        ==============
        get_birth_date
        ==============
        Return a birth date case where all parameters day/month/year
        are initialized
        """
        birth_date = False
        if day and month and year:
            try:
                birth_date = date(year, month, day)
            except:
                _logger.info('Reset `birth_date`: invalid date')
        return birth_date

    def get_partner_id(self, cr, uid, birth_date, lastname, firstname, email, context=None):
        """
        ==============
        get_partner_id
        ==============
        Make special combinations of domains to try to find
        a unique partner_id
        """
        partner_obj = self.pool['virtual.custom.partner']
        partner_domains = []

        if birth_date and email:
            partner_domains.append("[('is_company', '=', False),('birth_date', '=', '%s'),('email', '=', '%s')]" % (birth_date, email))
        if birth_date and email and firstname and lastname:
            partner_domains.append("[('is_company', '=', False),('birth_date', '=', '%s'),('email', '=', '%s'),('firstname', 'ilike', '%s'), ('lastname', 'ilike', '%s')]"\
                       % (birth_date, email, firstname, lastname))
        if email:
            partner_domains.append("[('is_company', '=', False),('email', '=', '%s')]" % (email))
        if firstname and lastname:
            partner_domains.append("[('is_company', '=', False),('firstname', 'ilike', '%s'),('lastname', 'ilike', '%s')]" % (firstname, lastname))

        partner_id = False
        virtual_partner_id = self.persist_search(cr, uid, partner_obj, partner_domains, context=context)
        # because this is not a real partner but a virtual partner
        if virtual_partner_id:
            partner_id = partner_obj.read(cr, uid, [virtual_partner_id], ['partner_id'])[0]
            partner_id = partner_id['partner_id'][0]
        return partner_id

    def get_technical_name(self, cr, uid, address_local_street_id, address_local_zip_id, \
        number, box, town_man, street_man, zip_man, country_id=False, context=None):
        """
        ==================
        get_technical_name
        ==================
        """
        if address_local_zip_id:
            zip_man, town_man = False, False
        if address_local_street_id:
            street_man = False
        address_local_zip = address_local_zip_id and self.pool['address.local.zip'].browse(cr, uid, [address_local_zip_id], context=context)[0].local_zip

        if not country_id:
            country_id = self.pool.get('res.country')._country_default_get(cr, uid, COUNTRY_CODE, context=context)
        values = OrderedDict([
            ('country_id', country_id),
            ('address_local_zip', address_local_zip),
            ('zip_man', zip_man),
            ('town_man', town_man),
            ('address_local_street_id', address_local_street_id),
            ('street_man', street_man),
            ('number', number),
            ('box', box),
        ])
        address_obj = self.pool['address.address']
        technical_name = address_obj._get_technical_name(cr, uid, values, context=context)
        return technical_name

    def get_phone_id(self, cr, uid, phone_number, phone_type, then_create=False, context=None):
        """
        =============
        get_number_id
        =============
        Try to find a `phone.phone` with name `number` and type `phone_type`
        :rtype: Integer or Boolean
        :rparam: Id of a `phone.phone` object or  False
        """
        phone_obj = self.pool['phone.phone']
        phone_ids = phone_obj.search(cr, uid, [('name', '=', phone_number), ('type', '=', '%s' % phone_type)])
        if not phone_ids and then_create:
            phone_ids.append(phone_obj.create(cr, uid, {'name': phone_number, 'type': phone_type}, context=context))
        return (phone_ids or False) and phone_ids[0]

    def get_format_email(self, cr, uid, email, context=None):
        """
        ================
        get_format_email
        ================
        ``Check and format`` email just like `email.coordinate` make it
        :rparam: formated email value
        """
        if email:
            email_obj = self.pool['email.coordinate']
            if email_obj._check_email_format(cr, uid, email, context=context) != None:
                email = email_obj.format_email(cr, uid, email, context=context)
        return email

    def get_format_phone_number(self, cr, uid, number, context=None):
        """
        =======================
        get_format_phone_number
        =======================
        Format a phone number with the same way as phone.phone do it.
        Call with a special context to avoid exception
        """
        if context is None:
            context = {}
        if number:
            ctx = context.copy()
            ctx.update({'install_mode': True})
            number = self.pool['phone.phone']._check_and_format_number(cr, uid, number, context=ctx)
        return number

    def pre_process(self, cr, uid, vals, context=None):
        """
        ===========
        pre_process
        ===========
        * Try to create a birth_date if all the components are there. (day/month/year)
        * Next step is to find partner by different way:
        ** birth_date + email
        ** birth_date + lastname + firstname
        ** email + firstname + lastname
        ** email
        ** firstname + lastname
        * Case of partner found: search email coordinate and phone coordinate for this partner

        :rparam vals: dictionary used to create ``membership_request``
        """
        if context is None:
            context = {}

        mobile_id = False
        phone_id = False

        firstname = vals.get('firstname', False)
        lastname = vals.get('lastname', False)
        day = vals.get('day', False)
        month = vals.get('month', False)
        year = vals.get('year', False)
        email = vals.get('email', False)
        mobile = vals.get('mobile', False)
        phone = vals.get('phone', False)
        address_local_street_id = vals.get('address_local_street_id', False)
        address_local_zip_id = vals.get('address_local_zip_id', False)
        number = vals.get('number', False)
        box = vals.get('box', False)
        town_man = vals.get('town_man', False)
        street_man = vals.get('street_man', False)
        zip_man = vals.get('zip_man', False)
        country_id = vals.get('country_id', False)
        partner_id = vals.get('partner_id', False)

        birth_date = self.get_birth_date(cr, uid, day, month, year, context=False)

        if mobile or phone:
            if mobile:
                mobile = self.get_format_phone_number(cr, uid, mobile, context=context)
                mobile_id = self.get_phone_id(cr, uid, mobile, 'mobile', context=context)
            if phone:
                phone = self.get_format_phone_number(cr, uid, phone, context=context)
                phone_id = self.get_phone_id(cr, uid, phone, 'fix', context=context)
        if email:
            email = self.get_format_email(cr, uid, email, context=context)
        if not partner_id:
            partner_id = self.get_partner_id(cr, uid, birth_date, lastname, firstname, email, context=False)

        technical_name = self.get_technical_name(cr, uid, address_local_street_id, address_local_zip_id,\
                                                 number, box, town_man, street_man, zip_man, country_id, context=context)

        # update vals dictionary because some inputs may have changed (and new values too)
        vals.update({
            'partner_id': partner_id,
            'lastname': lastname,
            'firstname': firstname,
            'birth_date': birth_date,
            'day': day,
            'month': month,
            'year': year,

            'mobile': mobile,
            'phone': phone,
            'email': email,

            'mobile_id': mobile_id,
            'phone_id': phone_id,
            'technical_name': technical_name,
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
        vals = {'state': 'confirm'}
        # superuser_id because of record rules
        return self.write(cr, SUPERUSER_ID, ids, vals, context=context)

    def validate_request(self, cr, uid, ids, context=None):
        """
        ================
        validate_request
        ================
        First check if the relations are set. For those try to update
        content
        In Other cases then create missing required data
        """
        for mr in self.browse(cr, uid, ids, context=context):
            # partner
            partner_values = {
                'lastname': mr.lastname,
                'firstname': mr.firstname,
                'gender': mr.gender,
                'birth_date': mr.birth_date,
            }
            if not mr.partner_id:
                partner_id = self.pool['res.partner'].create(cr, uid, partner_values, context=context)
            else:
                partner_id = mr.partner_id.id
            partner = self.pool['res.partner'].browse(cr, uid, [partner_id], context=context)[0]
            new_interests_ids = mr.interests_m2m_ids and ([interest.id for interest in mr.interests_m2m_ids]) or []
            #competencies
            new_competencies_ids = mr.competencies_m2m_ids and ([competence.id for competence in mr.competencies_m2m_ids]) or []

            partner_values.update({'competencies_m2m_ids': [[6, False, new_interests_ids]],
                               'interests_m2m_ids': [[6, False, new_competencies_ids]]})

            #update_partner values
            partner.write(partner_values)
            # address if technical name is empty then means that no address required
            address_id = mr.address_id and mr.address_id.id or False
            if not address_id and mr.technical_name != EMPTY_ADDRESS:
                address_values = {
                    'country_id': mr.country_id.id,
                    'street_man': False if mr.address_local_street_id else mr.street_man,
                    'zip_man': False if mr.address_local_zip_id else mr.zip_man,
                    'town_man': False if mr.address_local_zip_id else mr.town_man,
                    'address_local_street_id': mr.address_local_street_id and mr.address_local_street_id.id or False,
                    'address_local_zip_id': mr.address_local_zip_id and mr.address_local_zip_id.id or False,
                    'street2': mr.street2,
                    'number': mr.number,
                    'box': mr.box,
                    'sequence': mr.sequence,
                }
                address_id = self.pool['address.address'].create(cr, uid, address_values, context=context)
            if address_id:
                self.pool['postal.coordinate'].change_main_coordinate(cr, uid, [partner_id], address_id, context=context)

            # case of phone number
            self.change_main_phone(cr, uid, partner_id, mr.phone_id and mr.phone_id.id or False, mr.phone, 'fix', context=context)
            self.change_main_phone(cr, uid, partner_id, mr.mobile_id and mr.mobile_id.id or False, mr.mobile, 'mobile', context=context)

            # case of email
            if mr.email:
                self.pool['email.coordinate'].change_main_coordinate(cr, uid, [partner_id], mr.email, context=context)
        vals = {'state': 'validate'}
        # superuser_id because of record rules
        return self.write(cr, SUPERUSER_ID, ids, vals, context=context)

    def cancel_request(self, cr, uid, ids, context=None):
        pass

    def change_main_phone(self, cr, uid, partner_id, phone_id, phone_number, phone_type, context=None):
        if not phone_id:
            if phone_number:
                phone_id = self.get_phone_id(cr, uid, phone_number, phone_type, then_create=True, context=context)
        if phone_id:
            self.pool['phone.coordinate'].change_main_coordinate(cr, uid, [partner_id], phone_id, context=context)

# orm methods

    def create(self, cr, uid, vals, context=None):
        #do not pass related fields to the orm
        context = context or {}
        self._pop_related(cr, uid, vals, context=context)
        if context.get('install_mode', False) or context.get('mode', True) == 'ws':
            self.pre_process(cr, uid, vals, context=context)
        return super(membership_request, self).create(cr, uid, vals, context=context)

    def write(self, cr, uid, ids, vals, context=None):
        #do not pass related fields to the orm
        self._pop_related(cr, uid, vals, context=context)
        return super(membership_request, self).write(cr, uid, ids, vals, context=context)

    def name_get(self, cr, uid, ids, context=None):
        """
        display name is `lastname firstname`
        **Note**
        if firstname is empty then it is just lastname alone
        """
        if not ids:
            return []

        ids = isinstance(ids, (long, int)) and [ids] or ids

        res = []
        for record in self.browse(cr, uid, ids, context=context):
            display_name = '%s' % record.lastname if not record.firstname else\
                           '%s %s' % (record.lastname, record.firstname)
            res.append((record['id'], display_name))
        return res

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
