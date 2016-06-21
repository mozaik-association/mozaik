# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mozaik_membership, an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mozaik_membership is free software:
#     you can redistribute it and/or
#     modify it under the terms of the GNU Affero General Public License
#     as published by the Free Software Foundation, either version 3 of
#     the License, or (at your option) any later version.
#
#     mozaik_membership is distributed in the hope that it will
#     be useful but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the
#     GNU Affero General Public License
#     along with mozaik_membership.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from collections import OrderedDict
from contextlib import contextmanager
from datetime import date, datetime
from operator import attrgetter
from uuid import uuid4, uuid1
from dateutil.relativedelta import relativedelta

from openerp.addons.mozaik_address.address_address import COUNTRY_CODE
from openerp.addons.mozaik_base.base_tools import format_email, check_email
from openerp.addons.mozaik_base.base_tools import get_age
from openerp.addons.mozaik_person.res_partner import AVAILABLE_GENDERS
from openerp.osv import orm, fields
from openerp.tools import SUPERUSER_ID
from openerp.tools import logging
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT
from openerp.tools.translate import _
from openerp.exceptions import ValidationError
from openerp import api, fields as new_fields


_logger = logging.getLogger(__name__)

MEMBERSHIP_AVAILABLE_STATES = [
    ('draft', 'Draft'),
    ('confirm', 'Confirmed'),
    ('validate', 'Done'),
    ('cancel', 'Cancelled'),
]

EMPTY_ADDRESS = '0#0#0#0#0#0#0#0'
MEMBERSHIP_REQUEST_TYPE = [
    ('m', 'Member'),
    ('s', 'Supporter'),
]
MR_REQUIRED_AGE_KEY = 'mr_required_age'


class membership_request(orm.Model):

    _name = 'membership.request'
    _inherit = ['mozaik.abstract.model', 'abstract.term.finder']
    _description = 'Membership Request'
    _inactive_cascade = True
    _terms = ['interests_m2m_ids', 'competencies_m2m_ids']

    @api.multi
    @api.constrains('birth_date', 'age', 'state')
    def _check_age(self):
        required_age = int(self.env['ir.config_parameter'].get_param(
            MR_REQUIRED_AGE_KEY, default=16))
        if self.request_type and self.state == 'validate':
            if self.birth_date and self.age < required_age:
                raise ValidationError(
                    _('The required age for a membership request is %s') %
                    required_age)

    def _search_age(self, operator, value):
        """
        Use birth_date to search on age
        """
        age = value
        computed_birth_date = date.today() - relativedelta(years=age)
        computed_birth_date = datetime.strftime(
            computed_birth_date, DEFAULT_SERVER_DATE_FORMAT)
        if operator == '>=':
            operator = '<='
        elif operator == '<':
            operator = '>'
        return [('birth_date', operator, computed_birth_date)]

    @api.one
    @api.depends('is_company', 'birth_date')
    def _compute_age(self):
        """
        age computed depending of the birth date of the
        membership request
        """
        if not self.is_company and self.birth_date:
            self.age = get_age(self.birth_date)
        else:
            self.age = 0

    def _pop_related(self, cr, uid, vals, context=None):
        vals.pop('local_zip', None)
        vals.pop('country_code', None)
        vals.pop('identifier', None)

    def _get_membership_tracked_fields(self):
        '''
            This method return a list of tuple defining which fields
            must create a change record.
            Tuple is structured like:
             - sequence: n° of sequence of the change, it respect the display
                         order on the screen view
             - field name: field name on view
             - request path: path to the field value from the request object
             - partner_path: path to the field value from the partner object
             - label: label to be able to ignore comparison
        '''
        partner_address_path = 'postal_coordinate_id.address_id'
        return [
            (
                1,
                'lastname',
                'lastname',
                'lastname',
                ''
            ),
            (
                2,
                'firstname',
                'firstname',
                'firstname',
                ''
            ),
            (
                3,
                'birth_date',
                'birth_date',
                'birth_date',
                ''
            ),
            (
                4,
                'phone',
                'phone',
                'fix_coordinate_id.phone_id.name',
                ''
            ),
            (
                5,
                'gender',
                'gender',
                'gender',
                ''
            ),
            (
                6,
                'mobile',
                'mobile',
                'mobile_coordinate_id.phone_id.name',
                ''
            ),
            (
                7,
                'email',
                'email',
                'email_coordinate_id.email',
                ''
            ),
            (
                8,
                'country_id',
                'country_id.display_name',
                partner_address_path + '.country_id.display_name',
                ''
            ),
            # address_local_zip_id set on request AND on partner
            (
                9,
                'address_local_zip_id',
                'address_local_zip_id.display_name',
                partner_address_path + '.address_local_zip_id.display_name',
                'ZIP_REQUEST_PARTNER'
            ),
            # address_local_zip_id set on request AND not on partner
            (
                9,
                'address_local_zip_id',
                'address_local_zip_id.local_zip',
                partner_address_path + '.zip_man',
                'ZIP_REQUEST_NO_PARTNER'),
            (
                9,
                'address_local_zip_id',
                'address_local_zip_id.town',
                partner_address_path + '.town_man',
                'ZIP_REQUEST_NO_PARTNER'
            ),
            # address_local_zip_id not set on request but on partner
            (
                9,
                'zip_man',
                'zip_man',
                partner_address_path + '.address_local_zip_id.local_zip',
                'ZIP_NO_REQUEST_PARTNER'
            ),
            (
                9,
                'town_man',
                'town_man',
                partner_address_path + '.address_local_zip_id.town',
                'ZIP_NO_REQUEST_PARTNER'
            ),
            # address_local_zip_id not set on request and not on partner
            (
                9,
                'zip_man',
                'zip_man',
                partner_address_path + '.zip_man',
                'ZIP_NO_REQUEST_NO_PARTNER'),
            (
                9,
                'town_man',
                'town_man',
                partner_address_path + '.town_man',
                'ZIP_NO_REQUEST_NO_PARTNER'
            ),
            # address_local_street_id set on request AND on partner
            (
                10,
                'address_local_street_id',
                'address_local_street_id.display_name',
                partner_address_path + '.address_local_street_id.display_name',
                'STREET_REQUEST_PARTNER'
            ),
            # address_local_street_id set on request AND not on partner
            (
                10,
                'address_local_street_id',
                'address_local_street_id.display_name',
                partner_address_path + '.street_man',
                'ZIP_REQUEST_NO_PARTNER'
            ),
            # address_local_street_id not set on request but on partner
            (
                10,
                'street_man',
                'street_man',
                partner_address_path + '.address_local_street_id.display_name',
                'STREET_NO_REQUEST_PARTNER'
            ),
            # address_local_street_id not set on request and not partner
            (
                10,
                'street_man',
                'street_man',
                partner_address_path + '.street_man',
                'STREET_NO_REQUEST_NO_PARTNER'
            ),
            (
                11,
                'number',
                'number',
                partner_address_path + '.number',
                'NUMBER'
            ),
            (
                12,
                'street2',
                'street2',
                partner_address_path + '.street2',
                'STREET2'
            ),
            (
                13,
                'box',
                'box',
                partner_address_path + '.box',
                'BOX'
            ),
            (
                14,
                'sequence',
                'sequence',
                partner_address_path + '.sequence',
                'SEQUENCE'
            ),
            (
                15,
                'int_instance_id',
                'expr: request.force_int_instance_id.name or '
                'request.int_instance_id.name',
                'int_instance_id.name',
                ''
            ),
        ]

    def _clean_stored_changes(self, cr, uid, ids, context):
        chg_obj = self.pool.get('membership.request.change')
        chg_ids = chg_obj.search(cr, uid, [('membership_request_id',
                                            'in',
                                            ids)], context=context)
        if chg_ids:
            return chg_obj.unlink(cr, uid, chg_ids, context=context)

        return False

    def _get_labels_to_process(self, request):
        if not request.country_id:
            return []
        label_path = ['NUMBER', 'STREET2', 'BOX', 'SEQUENCE']
        partner_adr = request.partner_id.postal_coordinate_id.address_id
        if (request.address_local_zip_id and partner_adr.address_local_zip_id):
            label_path.append('ZIP_REQUEST_PARTNER')
        elif (request.address_local_zip_id and not
              partner_adr.address_local_zip_id):
            label_path.append('ZIP_REQUEST_NO_PARTNER')
        elif (not request.address_local_zip_id and
              partner_adr.address_local_zip_id):
            label_path.append('ZIP_NO_REQUEST_PARTNER')
        else:
            label_path.append('ZIP_NO_REQUEST_NO_PARTNER')

        if (request.address_local_street_id and
                partner_adr.address_local_street_id):
            label_path.append('STREET_REQUEST_PARTNER')
        elif (request.address_local_street_id and not
              partner_adr.address_local_street_id):
            label_path.append('STREET_REQUEST_NO_PARTNER')
        elif (not request.address_local_street_id and
              partner_adr.address_local_street_id):
            label_path.append('STREET_NO_REQUEST_PARTNER')
        else:
            label_path.append('STREET_NO_REQUEST_NO_PARTNER')
        return label_path

    def _detect_changes(self, cr, uid, ids, context=None):
        tracked_fields = self._get_membership_tracked_fields()
        fields_def = self.fields_get(
            cr, uid, [elem[1] for elem in tracked_fields], context=context)
        res = {}
        chg_obj = self.pool.get('membership.request.change')
        self._clean_stored_changes(cr, uid, ids, context=context)

        for request in self.browse(cr, uid, ids, context=context):
            if not request.partner_id:
                res[request.id] = False
                continue
            label_to_process = self._get_labels_to_process(request)

            for element in tracked_fields:
                seq, field, request_path, partner_path, label = element
                if label and label not in label_to_process:
                    continue
                if request_path.startswith('expr: '):
                    request_value = eval(request_path[6:])
                else:
                    request_value = attrgetter(request_path)(request)
                partner_value = attrgetter(partner_path)(request.partner_id)
                field = fields_def[field]

                if (request_value or label) and request_value != partner_value:
                    if 'selection' in field:
                        selection = dict(field['selection'])
                        request_value = selection.get(request_value)
                        partner_value = selection.get(partner_value)
                    vals = {
                        'membership_request_id': request.id,
                        'sequence': seq,
                        'field_name': field['string'],
                        'old_value': partner_value,
                        'new_value': request_value,
                    }
                    chg_obj.create(cr, uid, vals, context=context)

    def _get_status_values(self, request_type):
        """
        :type request_type: char
        :param request_type: m or s for member or supporter.
            `False` if not defined
        :rtype: dict
        :rparam: affected date resulting of the `request_type`
            and the `status`
        """
        vals = {}
        if request_type:
            vals['accepted_date'] = date.today().strftime('%Y-%m-%d')
            if request_type == 'm':
                vals['free_member'] = False
            elif request_type == 's':
                vals['free_member'] = True
        return vals

    _columns = {
        'identifier': fields.related('partner_id',
                                     'identifier',
                                     string='Identifier',
                                     type='integer'),
        'is_company': fields.boolean('Is a Company'),
        'lastname': fields.char('Name', required=True,
                                track_visibility='onchange'),
        'firstname': fields.char('Firstname', track_visibility='onchange'),

        'gender': fields.selection(AVAILABLE_GENDERS, 'Gender',
                                   select=True, track_visibility='onchange'),
        'email': fields.char('Email', track_visibility='onchange'),
        'phone': fields.char('Phone', track_visibility='onchange'),
        'mobile': fields.char('Mobile', track_visibility='onchange'),
        'day': fields.char('Day'),
        'month': fields.char('Month'),
        'year': fields.char('Year'),
        'birth_date': fields.date('Birth Date', track_visibility='onchange'),

        # request and states
        'request_type': fields.selection(MEMBERSHIP_REQUEST_TYPE,
                                         'Request Type',
                                         track_visibility='onchange'),
        'membership_state_id': fields.many2one('membership.state',
                                               'Current State'),
        'result_type_id': fields.many2one('membership.state',
                                          'Expected State'),
        'is_update': fields.boolean('Is Update'),
        'state': fields.selection(MEMBERSHIP_AVAILABLE_STATES,
                                  'State', track_visibility='onchange'),

        # address
        'country_id': fields.many2one('res.country', 'Country', select=True,
                                      track_visibility='onchange'),
        'country_code': fields.related('country_id', 'code',
                                       string='Country Code', type='char'),

        'address_local_zip_id': fields.many2one('address.local.zip',
                                                string='City',
                                                track_visibility='onchange'),
        'local_zip': fields.related('address_local_zip_id', 'local_zip',
                                    string='Local Zip', type='char'),
        'zip_man': fields.char(string='Zip', track_visibility='onchange'),

        'town_man': fields.char(string='Town', track_visibility='onchange'),

        'address_local_street_id': fields.many2one(
            'address.local.street', string='Reference Street',
            track_visibility='onchange'),
        'street_man': fields.char(string='Street',
                                  track_visibility='onchange'),
        'street2': fields.char(string='Street2',
                               track_visibility='onchange'),

        'number': fields.char(string='Number', track_visibility='onchange'),
        'box': fields.char(string='Box', track_visibility='onchange'),
        'sequence': fields.integer('Sequence',
                                   track_visibility='onchange',
                                   group_operator='min'),

        'technical_name': fields.char(string='Technical Name'),

        # indexes
        'interests': fields.text(string='Interests'),
        'competencies': fields.text(string='Competencies'),

        'interests_m2m_ids': fields.many2many(
            'thesaurus.term', 'membership_request_interests_rel',
            id1='membership_id', id2='thesaurus_term_id', string='Interests'),
        'competencies_m2m_ids': fields.many2many(
            'thesaurus.term', 'membership_request_competence_rel',
            id1='membership_id', id2='thesaurus_term_id',
            string='Competencies'),

        'note': fields.text('Notes'),

        # references
        'partner_id': fields.many2one(
            'res.partner', string='Partner', ondelete='cascade',
            domain="[('membership_state_id', '!=', False)]"),

        'int_instance_id': fields.many2one(
            'int.instance',
            string='Internal Instance',
            ondelete='cascade'
        ),
        'force_int_instance_id': fields.many2one(
            'int.instance',
            string='Internal Instance (to Force)',
            ondelete='cascade',
            track_visibility='onchange',
        ),

        'address_id': fields.many2one('address.address',
                                      string='Address',
                                      track_visibility='onchange'),
        'mobile_id': fields.many2one('phone.phone',
                                     string='Mobile',
                                     track_visibility='onchange'),
        'phone_id': fields.many2one('phone.phone',
                                    string='Phone',
                                    track_visibility='onchange'),
        'change_ids': fields.one2many('membership.request.change',
                                      'membership_request_id',
                                      string='Changes',
                                      domain=[('active', '=', True)]),
        'inactive_change_ids': fields.one2many('membership.request.change',
                                               'membership_request_id',
                                               string='Changes',
                                               domain=[('active',
                                                        '=', False)]),
    }

    age = new_fields.Integer(
        string='Age', compute='_compute_age', search='_search_age')
    replace_coordinates = new_fields.Boolean(
        string='Replace Coordinates', default=True)

    _defaults = {
        'is_company': False,
        'is_update': False,
        'state': 'draft',
    }

    _order = 'id desc'

# constraints

    _unicity_keys = 'N/A'

# view methods: onchange, button

    def onchange_country_id(self, cr, uid, ids, country_id, zip_man, town_man,
                            street_man, number, box, context=None):
        uid = SUPERUSER_ID
        return {
            'value': {
                'country_code': self.pool.get('res.country').read(
                    cr, uid, [country_id], ['code'],
                    context=context)[0]['code'] if country_id else False,
                'address_local_zip_id': False,
                'technical_name': self.get_technical_name(
                    cr, uid, False, False,
                    number, box, town_man, street_man, zip_man, country_id,
                    context=context),
                'int_instance_id': self.get_int_instance_id(
                    cr, uid, False, context=context)
            }
        }

    def onchange_local_zip_id(self, cr, uid, ids, country_id,
                              address_local_zip_id, zip_man, town_man,
                              street_man, number, box, context=None):
        uid = SUPERUSER_ID
        # local_zip used for domain
        local_zip = False
        if address_local_zip_id:
            local_zip = self.pool['address.local.zip'].browse(
                cr, uid, [address_local_zip_id], context=context)[0].local_zip
        return {
            'value': {
                'address_local_street_id': False,
                'technical_name': self.get_technical_name(
                    cr, uid, False, address_local_zip_id,
                    number, box, town_man, street_man, zip_man,
                    country_id, context=context),
                'local_zip': local_zip,
                'int_instance_id': self.get_int_instance_id(
                    cr, uid, address_local_zip_id, context=context)
            }
        }

    def onchange_other_address_componants(self, cr, uid, ids,
                                          country_id, address_local_zip_id,
                                          zip_man, town_man,
                                          address_local_street_id, street_man,
                                          number, box, context=None):
        uid = SUPERUSER_ID
        return {
            'value': {
                'technical_name': self.get_technical_name(
                    cr, uid, address_local_street_id, address_local_zip_id,
                    number, box, town_man, street_man, zip_man, country_id,
                    context=context)
            }
        }

    def onchange_technical_name(self, cr, uid, ids, technical_name,
                                context=None):
        uid = SUPERUSER_ID
        address_ids = self.pool['address.address'].search(
            cr, uid, [('technical_name', '=', technical_name)],
            context=context)
        return {
            'value': {
                'address_id': address_ids and address_ids[0] or False
            }
        }

    def onchange_partner_component(self, cr, uid, ids, is_company,
                                   day, month, year,
                                   lastname, firstname, email, is_update,
                                   context=None):
        """
        try to find a new partner_id depending of the
        birth_date, lastname, firstname, email
        """
        uid = SUPERUSER_ID
        birth_date = False
        if not is_company:
            birth_date = self.get_birth_date(cr, uid, day, month, year,
                                             context=context)
        email = self.get_format_email(cr, uid, email, context=context)
        values = {
            'value': {
                'birth_date': '%s' % birth_date if birth_date else False,
                'email': email,
            }
        }
        if is_update:
            return values

        partner_id = self.get_partner_id(cr, uid, is_company, birth_date,
                                         lastname, firstname, email,
                                         context=context)
        values['value'].update({
            'partner_id': partner_id,
        })
        return values

    def onchange_partner_id(self, cr, uid, ids,
                            is_company, request_type, partner_id,
                            technical_name, context=None):
        """
        Take current
            * membership_state_id
            * interests_m2m_ids
            * competencies_m2m_ids
        of ``partner_id``
        And set corresponding fields into the ``membership.request``

        **Note**
        fields are similarly named
        """
        uid = SUPERUSER_ID
        res = {
            'interests_m2m_ids': False,
            'competencies_m2m_ids': False,
            'identifier': False,
        }
        if partner_id:
            res_partner_obj = self.pool['res.partner']
            partner = res_partner_obj.browse(cr, uid, partner_id,
                                             context=context)
            # take current status of partner
            partner_status_id = partner.membership_state_id and \
                partner.membership_state_id.id or False
            interests_ids = [term.id for term in partner.interests_m2m_ids]
            res['interests_m2m_ids'] = interests_ids and \
                [[6, False, interests_ids]] or \
                False
            competencies_ids = [trm.id for trm in partner.competencies_m2m_ids]
            res['competencies_m2m_ids'] = competencies_ids and \
                [[6, False, competencies_ids]] or \
                False
            res['identifier'] = partner.identifier

            if technical_name == EMPTY_ADDRESS:
                res['int_instance_id'] = partner.int_instance_id.id
        else:
            partner_status_id = self.pool['membership.state'].\
                _state_default_get(cr, uid, context=context)

        result_type_id = False
        if not is_company:
            result_type_id = self.get_partner_preview(
                cr, uid, request_type, partner_id, context=context)
        elif request_type:
            res.update({
                'request_type': False,
            })

        res.update({
            'membership_state_id': partner_status_id,
            'result_type_id': result_type_id,
        })
        return {'value': res}

    def onchange_mobile(self, cr, uid, ids, mobile, context=None):
        mobile = self.get_format_phone_number(cr, uid, mobile, context=context)
        mobile_id = self.get_phone_id(cr, uid, mobile, 'mobile',
                                      context=context)
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

    @contextmanager
    def protect_v8_cache(self):
        '''
        Hackish: prevent to alter the _cache of onchange record
        when simulating a workflow progression on an onchange callback
        '''
        orig_pure_fct_fields = self.pool.pure_function_fields
        self.pool.pure_function_fields = []
        try:
            yield
        except:
            raise
        finally:
            self.pool.pure_function_fields = orig_pure_fct_fields

    def get_partner_preview(
            self,
            cr,
            uid,
            request_type,
            partner_id=False,
            context=None):
        """
        Advance partner's workflow to catch the next state
        If no partner then create one
        See also write and create method in abstract_model, it is important
        that disable_tracking remains always True during the entire simulation
        :type request_type: char
        :param request_type: m or s (member or supporter)
        :type partner_id: integer
        :param partner_id: id of partner
        :rparam: next status in partner's workflow depending on `request_type`
        """
        context = context or {}

        partner_obj = self.pool['res.partner']

        status_id = False
        name = 'preview-%s' % uuid1().hex
        cr.execute('SAVEPOINT "%s"' % name)
        try:
            if not partner_id:
                partner_datas = {
                    'lastname': '%s' % uuid4(),
                    'identifier': -1,
                }
                with self.protect_v8_cache():
                    # safe mode is here mandatory
                    partner_id = partner_obj.create(
                        cr, uid, partner_datas, context=context)
            status_id = partner_obj.read(
                cr, uid, partner_id, ['membership_state_id'],
                context=context)['membership_state_id'][0]
            vals = self._get_status_values(request_type)
            if vals:
                with self.protect_v8_cache():
                    # safe mode is here mandatory
                    partner_obj.write(
                        cr, uid, partner_id, vals, context=context)
                status_id = partner_obj.read(
                    cr, uid, partner_id, ['membership_state_id'],
                    context=context)['membership_state_id'][0]
        except:
            pass
        finally:
            cr.execute('ROLLBACK TO SAVEPOINT "%s"' % name)

        return status_id

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
                birth_date = date(
                    int(year), int(month), int(day)).strftime('%Y-%m-%d')
            except:
                _logger.info('Reset `birth_date`: Invalid Date')
        return birth_date

    def get_partner_id(self, cr, uid, is_company, birth_date,
                       lastname, firstname, email,
                       context=None):
        """
        Make special combinations of domains to try to find
        a unique partner_id
        """
        partner_obj = self.pool['virtual.custom.partner']
        partner_domains = []

        if not is_company and birth_date and email and firstname and lastname:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('birth_date','=', '%s'),"
                "('email', '=', '%s'),"
                "(\"firstname\", 'ilike', \"%s\"),"
                "(\"lastname\", 'ilike', \"%s\")]"
                % (birth_date, email, firstname, lastname))
        if not is_company and birth_date and email:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('birth_date','=', '%s'),"
                "('email', '=', '%s')]" % (birth_date, email))
        if not is_company and email:
            partner_domains.append(
                "[('membership_state_id', '!=', False),"
                "('is_company', '=', False),"
                "('email', '=','%s')]" % (email))
        if is_company and email:
            partner_domains.append(
                "[('is_company', '=', True),"
                "('email', '=','%s')]" % (email))
        if lastname:
            if not is_company and firstname:
                partner_domains.append(
                    "[('membership_state_id','!=',False),"
                    "('is_company', '=', False),"
                    "(\"firstname\", 'ilike', \"%s\"),"
                    "(\"lastname\", 'ilike', \"%s\")]" % (firstname, lastname))
            elif not is_company:
                partner_domains.append(
                    "[('membership_state_id', '!=', False),"
                    "('is_company', '=', False),"
                    "(\"lastname\", 'ilike', \"%s\")]" % (lastname))
            else:
                partner_domains.append(
                    "[('is_company', '=', True),"
                    "(\"lastname\", 'ilike', \"%s\")]" % (lastname))

        partner_id = False
        virtual_partner_id = self.persist_search(cr, uid, partner_obj,
                                                 partner_domains,
                                                 context=context)
        # because this is not a real partner but a virtual partner
        if virtual_partner_id:
            partner_id = partner_obj.read(cr, uid, [virtual_partner_id],
                                          ['partner_id'])[0]
            partner_id = partner_id['partner_id'][0]
        return partner_id

    def persist_search(self, cr, uid, model_obj, domains, context=None):
        """
        This method will make a search with a list of domain and return result
        only if it is a single result
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
                try:
                    domain = eval(domains[loop_counter])
                except:
                    raise orm.except_orm(_('Error'), _('Invalid Data'))
                model_ids = model_obj.search(cr, uid, domain, context=context)
                if len(model_ids) == 1:
                    return model_ids[0]
                else:
                    return rec_search(loop_counter + 1)

        return rec_search(0)

    def get_technical_name(self, cr, uid, address_local_street_id,
                           address_local_zip_id, number, box, town_man,
                           street_man, zip_man, country_id,
                           context=None):
        if not country_id:
            return EMPTY_ADDRESS
        local_zip = False
        if address_local_zip_id:
            zip_man, town_man = False, False
            local_zip = self.pool['address.local.zip'].browse(
                cr, uid, [address_local_zip_id], context=context)[0].local_zip
        if address_local_street_id:
            street_man = False
        values = OrderedDict([
            ('country_id', country_id),
            ('address_local_zip', local_zip),
            ('zip_man', zip_man),
            ('town_man', town_man),
            ('address_local_street_id', address_local_street_id),
            ('street_man', street_man),
            ('number', number),
            ('box', box),
        ])
        address_obj = self.pool['address.address']
        technical_name = address_obj._get_technical_name(cr, uid, values,
                                                         context=context)
        return technical_name

    def get_phone_id(self, cr, uid, phone_number, phone_type,
                     then_create=False, context=None):
        """
        Try to find a `phone.phone` with name `number` and type `phone_type`
        :rtype: Integer or Boolean
        :rparam: Id of a `phone.phone` object or  False
        """
        phone_obj = self.pool['phone.phone']
        wiz_obj = self.pool['change.phone.type']
        phone_ids = phone_obj.search(cr, uid, [('name', '=', phone_number),
                                               ('type', '=', '%s'
                                                % phone_type)])
        if not phone_ids and then_create:
            phone_ids = phone_obj.search(
                cr, uid, [('name', '=', phone_number)])
            if phone_ids:
                wiz_id = wiz_obj.create(
                    cr, uid, {'phone_id': phone_ids[0], 'type': phone_type})
                wiz_obj.change_phone_type(cr, uid, wiz_id, context=context)
            else:
                phone_ids.append(phone_obj.create(
                    cr, uid, {'name': phone_number, 'type': phone_type},
                    context=context))
        return (phone_ids or False) and phone_ids[0]

    def get_format_email(self, cr, uid, email, context=None):
        """
        ``Check and format`` email just like `email.coordinate` make it
        :rparam: formated email value
        """
        if email:
            if check_email(email):
                email = format_email(email)
        return email

    def get_format_phone_number(self, cr, uid, number, context=None):
        """
        Format a phone number with the same way as phone.phone do it.
        Call with a special context to avoid exception
        """
        if context is None:
            context = {}
        if number:
            ctx = context.copy()
            ctx.update({'install_mode': True})
            number = self.pool['phone.phone']._check_and_format_number(
                cr, uid, number, context=ctx)
        return number

    def pre_process(self, cr, uid, vals, context=None):
        """
        * Try to create a birth_date if all the components are there.
        (day/month/year)
        * Next step is to find partner by different way:
        ** birth_date + email
        ** birth_date + lastname + firstname
        ** email + firstname + lastname
        ** email
        ** firstname + lastname
        * Case of partner found: search email coordinate and phone coordinate
        for this partner

        :rparam vals: dictionary used to create ``membership_request``
        """
        if context is None:
            context = {}

        mobile_id = False
        phone_id = False

        is_company = vals.get('is_company', False)
        firstname = False if is_company else vals.get('firstname', False)
        lastname = vals.get('lastname', False)
        birth_date = False if is_company else vals.get('birth_date', False)
        day = False if is_company else vals.get('day', False)
        month = False if is_company else vals.get('month', False)
        year = False if is_company else vals.get('year', False)
        gender = False if is_company else vals.get('gender', False)
        email = vals.get('email', False)
        mobile = vals.get('mobile', False)
        phone = vals.get('phone', False)
        address_id = vals.get('address_id', False)
        address_local_street_id = vals.get('address_local_street_id', False)
        address_local_zip_id = vals.get('address_local_zip_id', False)
        number = vals.get('number', False)
        box = vals.get('box', False)
        town_man = vals.get('town_man', False)
        country_id = vals.get('country_id', False)
        zip_man = vals.get('zip_man', False)
        street_man = vals.get('street_man', False)

        partner_id = vals.get('partner_id', False)

        request_type = vals.get('request_type', False)

        if zip_man and town_man:
            domain = [
                ('local_zip', '=', zip_man),
                ('town', 'ilike', town_man),
            ]
            zids = self.pool['address.local.zip'].search(
                cr, uid, domain, context=context)
            if zids:
                cnty_id = self.pool['res.country']._country_default_get(
                    cr, uid, COUNTRY_CODE, context=context)
                if not country_id or cnty_id == country_id:
                    country_id = cnty_id
                    address_local_zip_id = zids[0]
                    town_man = False
                    zip_man = False

        if not is_company and not birth_date:
            birth_date = self.get_birth_date(cr, uid, day, month, year,
                                             context=context)

        if mobile:
            mobile = self.get_format_phone_number(cr, uid, mobile,
                                                  context=context)
            mobile_id = self.get_phone_id(cr, uid, mobile, 'mobile',
                                          context=context)
        if phone:
            phone = self.get_format_phone_number(cr, uid, phone,
                                                 context=context)
            phone_id = self.get_phone_id(cr, uid, phone, 'fix',
                                         context=context)
        if email:
            email = self.get_format_email(cr, uid, email, context=context)

        if not partner_id:
            partner_id = self.get_partner_id(cr, uid, is_company, birth_date,
                                             lastname, firstname, email,
                                             context=context)

        technical_name = self.get_technical_name(
            cr, uid, address_local_street_id, address_local_zip_id, number,
            box, town_man, street_man, zip_man, country_id,
            context=context)
        address_id = address_id or self.onchange_technical_name(
            cr, uid, False, technical_name,
            context=context)['value']['address_id']
        int_instance_id = self.get_int_instance_id(
            cr, uid, address_local_zip_id, context=context)

        res = self.onchange_partner_id(
            cr, uid, [], is_company, request_type, partner_id, technical_name,
            context=None)['value']
        vals.update(res)

        # update vals dictionary because some inputs may have changed
        # (and new values too)
        vals.update({
            'is_company': is_company,
            'partner_id': partner_id,

            'lastname': lastname,
            'firstname': firstname,
            'birth_date': birth_date,

            'int_instance_id': int_instance_id,

            'day': day,
            'month': month,
            'year': year,
            'gender': gender,

            'mobile': mobile,
            'phone': phone,
            'email': email,

            'mobile_id': mobile_id,
            'phone_id': phone_id,

            'address_id': address_id,
            'address_local_zip_id': address_local_zip_id,
            'country_id': country_id,
            'zip_man': zip_man,
            'town_man': town_man,

            'technical_name': technical_name,
        })

        return vals

    def confirm_request(self, cr, uid, ids, context=None):
        vals = {
            'state': 'confirm'
        }
        # superuser_id because of record rules
        return self.write(cr, SUPERUSER_ID, ids, vals, context=context)

    def validate_request(self, cr, uid, ids, context=None):
        """
        First check if the relations are set. For those try to update
        content
        In Other cases then create missing required data
        """
        cntx = context
        mr_vals = {}
        partner_obj = self.pool['res.partner']
        for mr in self.browse(cr, uid, ids, context=context):
            context = dict(cntx or {})
            partner_values = {
                'is_company': mr.is_company,
                'lastname': mr.lastname,
            }
            if not mr.is_company:
                partner_values['firstname'] = mr.firstname
                if mr.gender:
                    partner_values['gender'] = mr.gender
                if mr.birth_date:
                    partner_values['birth_date'] = mr.birth_date

            result_id = mr.result_type_id and mr.result_type_id.id or False

            new_instance_id = \
                mr.force_int_instance_id.id or mr.int_instance_id.id
            if mr.is_company or mr.membership_state_id.id != result_id:
                partner_values['int_instance_id'] = new_instance_id
            if mr.force_int_instance_id and \
                    mr.force_int_instance_id.id != mr.int_instance_id.id:
                partner_values['int_instance_id'] = new_instance_id
                context['keep_current_instance'] = True

            new_interests_ids = []
            if not mr.is_company:
                new_interests_ids = mr.interests_m2m_ids and \
                    ([interest.id for interest in mr.interests_m2m_ids]) or []
            new_competencies_ids = mr.competencies_m2m_ids and \
                ([competence.id for competence in mr.competencies_m2m_ids]) \
                or []

            notes = []
            if mr.note:
                notes.append(mr.note)
            if mr.partner_id and mr.partner_id.comment:
                notes.append(mr.partner_id.comment)

            partner_values.update({
                'competencies_m2m_ids': [[6, False, new_competencies_ids]],
                'interests_m2m_ids': [[6, False, new_interests_ids]],
                'comment': notes and '\n'.join(notes) or False,
            })

            # update_partner values
            # Passing do_not_track_twice in context the first tracking
            # evaluation through workflow will produce a notification
            # the second one out of workflow not (when context will be
            # pass through workflow this solution will not work anymore)
            ctx = dict(context, do_not_track_twice=True)

            upd_folw = False
            if mr.partner_id:
                partner_id = mr.partner_id.id
                if mr.partner_id.int_instance_id.id != new_instance_id:
                    context['new_instance_id'] = new_instance_id
                    partner_obj._subscribe_assemblies(
                        cr, uid, partner_id, context=context)
                    upd_folw = True
            else:
                partner_id = partner_obj.create(cr, uid, partner_values,
                                                context=context)
                mr_vals['partner_id'] = partner_id
                partner_values = {}

            if not mr.is_company:
                partner_values.update(
                    self._get_status_values(mr.request_type))
            if partner_values:
                partner_obj.write(
                    cr, uid, [partner_id], partner_values, context=ctx)
            if upd_folw:
                if mr.membership_state_id.id == result_id:
                    partner_obj.update_membership_line(
                        cr, uid, [partner_id], context=context)
                partner_obj._update_followers(
                    cr, SUPERUSER_ID, [partner_id], context=context)

            # address if technical name is empty then means that no address
            # required
            address_id = mr.address_id and mr.address_id.id or False
            if not address_id and \
                    mr.technical_name and mr.technical_name != EMPTY_ADDRESS:
                address_values = {
                    'country_id': mr.country_id.id,
                    'street_man': False if mr.address_local_street_id else
                    mr.street_man,
                    'zip_man': False if mr.address_local_zip_id else
                    mr.zip_man,
                    'town_man': False if mr.address_local_zip_id else
                    mr.town_man,
                    'address_local_street_id': mr.address_local_street_id and
                    mr.address_local_street_id.id or False,
                    'address_local_zip_id': mr.address_local_zip_id and
                    mr.address_local_zip_id.id or False,
                    'street2': mr.street2,
                    'number': mr.number,
                    'box': mr.box,
                    'sequence': mr.sequence,
                }
                address_id = self.pool['address.address'].create(
                    cr, uid, address_values, context=context)
                mr_vals['address_id'] = address_id

            context['invalidate'] = mr.replace_coordinates

            if address_id:
                self.pool['postal.coordinate'].change_main_coordinate(
                    cr, uid, [partner_id], address_id, context=context)

            # case of phone number
            mr_vals['phone_id'] = self.change_main_phone(
                cr, uid, partner_id, mr.phone_id and mr.phone_id.id or False,
                mr.phone, 'fix', context=context)
            mr_vals['mobile_id'] = self.change_main_phone(
                cr, uid, partner_id,
                mr.mobile_id and mr.mobile_id.id or False,
                mr.mobile, 'mobile', context=context)

            # case of email
            if mr.email:
                self.pool['email.coordinate'].change_main_coordinate(
                    cr, uid, [partner_id], mr.email, context=context)

        # if request `validate` then object should be invalidate
        mr_vals.update({'state': 'validate'})
        # superuser_id because of record rules
        self.action_invalidate(cr, SUPERUSER_ID, ids, context=context,
                               vals=mr_vals)
        return True

    def cancel_request(self, cr, uid, ids, context=None):
        # superuser_id because of record rules
        self.action_invalidate(cr, SUPERUSER_ID, ids, context=context,
                               vals={'state': 'cancel'})
        return True

    def change_main_phone(self, cr, uid, partner_id, phone_id, phone_number,
                          phone_type, context=None):
        if not phone_id:
            if phone_number:
                phone_id = self.get_phone_id(cr, uid, phone_number, phone_type,
                                             then_create=True, context=context)
        if phone_id:
            self.pool['phone.coordinate'].change_main_coordinate(
                cr, uid, [partner_id], phone_id, context=context)

        return phone_id

    def get_int_instance_id(
            self, cr, uid, address_local_zip_id, context=None):
        '''
        :rtype: integer
        :rparam: instance id of address local zip or default instance id if
            `address_local_zip_id` is False
        '''
        if address_local_zip_id:
            zip_obj = self.pool['address.local.zip']
            zip_rec = zip_obj.browse(
                cr, uid, address_local_zip_id, context=context)
            return zip_rec.int_instance_id.id
        else:
            instance_obj = self.pool['int.instance']
            return instance_obj.get_default(cr, uid)

    def update_changes(self, cr, uid, ids, context=None):
        return

# orm methods

    def create(self, cr, uid, vals, context=None):
        # do not pass related fields to the orm
        context = context or {}

        if context.get('install_mode', False) or \
                context.get('mode', True) == 'ws':
            self.pre_process(cr, uid, vals, context=context)

        self._pop_related(cr, uid, vals, context=context)
        request_id = super(membership_request, self).create(cr, uid, vals,
                                                            context=context)
        self._detect_changes(cr, uid, [request_id], context=context)

        return request_id

    def write(self, cr, uid, ids, vals, context=None):
        # do not pass related fields to the orm
        ids = isinstance(ids, (long, int)) and [ids] or ids
        active_ids = self.search(cr, uid,
                                 [('id', 'in', ids), ('active', '=', True)],
                                 context=context)
        self._pop_related(cr, uid, vals, context=context)
        res = super(membership_request, self).write(cr, uid, ids, vals,
                                                    context=context)
        if 'active' in vals:
            if not vals.get('active'):
                active_ids = []
        if active_ids:
            self._detect_changes(cr, uid, active_ids, context=context)
        return res

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


class membership_request_change(orm.Model):
    _name = 'membership.request.change'
    _inherit = ['mozaik.abstract.model']
    _description = 'Membership Request Change'
    _order = 'sequence'

    _columns = {
        'membership_request_id': fields.many2one(
            'membership.request', 'Membership Request', ondelete='cascade'),
        'sequence': fields.integer('Sequence'),
        'field_name': fields.char('Field Name'),
        'old_value': fields.char('Old Value'),
        'new_value': fields.char('New Value'),
    }

    _unicity_keys = 'N/A'
