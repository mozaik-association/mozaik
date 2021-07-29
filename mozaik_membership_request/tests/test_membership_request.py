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
from datetime import date, datetime
from uuid import uuid4

from anybox.testing.openerp import SharedSetupTransactionCase
from dateutil.relativedelta import relativedelta

from openerp.addons.mozaik_membership.membership_request\
    import MR_REQUIRED_AGE_KEY
from openerp.addons.mozaik_address.address_address import COUNTRY_CODE
from openerp.exceptions import ValidationError
from openerp.tools.misc import DEFAULT_SERVER_DATE_FORMAT


class test_membership(SharedSetupTransactionCase):

    _data_files = (
        # load the partner
        '../../mozaik_base/tests/data/res_partner_data.xml',
        # load structures
        '../../mozaik_structure/tests/data/structure_data.xml',
        # load address of this partner
        '../../mozaik_address/tests/data/reference_data.xml',
        # load postal_coordinate of this partner
        '../../mozaik_address/tests/data/address_data.xml',
        # load phone_coordinate of this partner
        '../../mozaik_phone/tests/data/phone_data.xml',
        # load terms and requests
        '../../mozaik_thesaurus/tests/data/thesaurus_data.xml',
        'data/membership_request_data.xml',
    )

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_membership, self).setUp()
        self.env.clear()
        self.partner_obj = self.registry['res.partner']

        self.mro = self.registry('membership.request')
        self.mrco = self.registry('membership.request.change')
        self.mrs = self.registry('membership.state')

        self.rec_partner = self.browse_ref(
            '%s.res_partner_thierry' % self._module_ns)
        self.rec_partner_pauline = self.browse_ref(
            '%s.res_partner_pauline' % self._module_ns)
        self.rec_partner_jacques = self.browse_ref(
            '%s.res_partner_jacques' % self._module_ns)
        self.rec_postal = self.browse_ref(
            '%s.postal_coordinate_2_duplicate_2' % self._module_ns)
        self.rec_phone = self.browse_ref(
            '%s.main_mobile_coordinate_two' % self._module_ns)

        self.rec_mr_update = self.browse_ref(
            '%s.membership_request_mp' % self._module_ns)
        self.rec_mr_create = self.browse_ref(
            '%s.membership_request_eh' % self._module_ns)
        self.mobile_five = self.browse_ref('%s.mobile5'
                                           % self._module_ns)
        self.coord_mobile_2 = self.browse_ref(
            '%s.mobile_coordinate_for_jacques_2' % self._module_ns)

    def test_pre_process(self):
        """
        Test that input values to create a ``membership.request``
        are found and matched with existing data
        """
        cr, uid, context = self.cr, self.uid, {}

        base_values = {
            'lastname': self.rec_partner.lastname,
            'firstname': self.rec_partner.firstname,
            'gender': self.rec_partner.gender,
            'day': 1,
            'month': 04,
            'year': 1985,

            'request_type': 's',
            'mobile': self.rec_phone.phone_id.name,
        }
        all_values = {
            'street':
            self.rec_postal.address_id.address_local_street_id.local_street,
            'zip_man':
            self.rec_postal.address_id.address_local_zip_id.local_zip,
            'address_local_street_id':
            self.rec_postal.address_id.address_local_street_id.id,
            'box': self.rec_postal.address_id.box,
            'number': self.rec_postal.address_id.number,
            'town_man': self.rec_postal.address_id.address_local_zip_id.town,
        }
        all_values.update(base_values)

        output_values = self.mro._pre_process(
            cr, uid, all_values, context=context)
        self.assertEqual(output_values.get('mobile_id', False),
                         self.rec_phone.phone_id.id,
                         'Should have the same phone that the phone of the \
                         phone coordinate')
        self.assertEqual(output_values.get('address_id', False),
                         self.rec_postal.address_id.id,
                         'Should be the same address')
        self.assertEqual(output_values.get('partner_id', False),
                         self.rec_partner.id, 'Should have the same partner')
        self.assertEqual(
            output_values.get('int_instance_id', False),
            self.rec_postal.address_id.address_local_zip_id.int_instance_id.id,
            'Instance should be the instance of the address local zip')
        output_values = self.mro._pre_process(
            cr, uid, base_values, context=context)
        self.assertEqual(
            output_values.get('int_instance_id', False),
            self.rec_partner.int_instance_id.id,
            'Instance should be the instance of the partner')

    def test_get_address_id(self):
        cr, uid = self.cr, self.uid
        adrs = self.browse_ref('%s.address_3' % self._module_ns)
        address_local_street_id = adrs.address_local_street_id and \
            adrs.address_local_street_id.id
        address_local_zip_id = adrs.address_local_zip_id and \
            adrs.address_local_zip_id.id
        country_id = adrs.country_id and adrs.country_id.id
        technical_name = self.mro.get_technical_name(
            cr, uid, address_local_street_id, address_local_zip_id,
            adrs.number, adrs.box, adrs.town_man, adrs.street_man,
            adrs.zip_man, country_id)
        waiting_adrs_ids = self.registry['address.address'].search(
            cr, uid, [('technical_name', '=', technical_name)])
        waiting_adrs_id = -1
        if waiting_adrs_ids:
            waiting_adrs_id = waiting_adrs_ids[0]
        self.assertEqual(adrs.id, waiting_adrs_id,
                         'Address id Should be the same')

    def test_voluntaries(self):
        """
        * Test the validate process and check for
        ** regional_voluntary and local_only
        """
        mr_obj = self.env['membership.request']

        vals = {
            'firstname': 'Virginie',
            'lastname': 'EFIRA',
        }

        # create and validate a membership request
        mr = mr_obj.create(vals)
        mr.validate_request()
        partner = mr.partner_id
        self.assertFalse(partner.local_only)

        # create membership request from the partner
        mr_id = partner.button_modification_request()['res_id']
        mr = mr_obj.browse([mr_id])

        vals = {
            'local_only': True,
        }
        mr.write(vals)
        self.assertTrue(mr.local_only)

        # validate the request
        mr.validate_request()
        self.assertTrue(partner.local_only)

        # create membership request from the partner
        mr_id = partner.button_modification_request()['res_id']
        mr = mr_obj.browse([mr_id])

        vals = {
            'request_type': 's',
        }
        vals.update(mr.onchange_partner_id(
            mr.is_company, 's', partner.id, mr.technical_name)['value'])
        mr.write(vals)
        self.assertFalse(mr.local_only)

        # validate the request
        mr.validate_request()
        self.assertFalse(partner.local_only)

        # create membership request from the partner
        mr_id = partner.button_modification_request()['res_id']
        mr = mr_obj.browse([mr_id])

        vals = {
            'request_type': 'm',
        }
        vals.update(mr.onchange_partner_id(
            mr.is_company, 'm', partner.id, mr.technical_name)['value'])
        vals['regional_voluntary'] = True
        mr.write(vals)
        self.assertTrue(mr.regional_voluntary)

        # validate the request
        mr.validate_request()
        self.assertTrue(partner.regional_voluntary)

        return

    def test_validate_request(self):
        """
        * Test the validate process with an update and check for
        ** firstname
        ** email
        ** mobile
        ** amount and reference
        ** not loss of original birthdate (mr do never reset fields)
        * Test the validate process with a create and check that
            relations are created
        """
        cr, uid = self.cr, self.uid
        partner_obj = self.registry['res.partner']
        congo = self.ref('base.cd')

        # 1. partner to update
        mr = self.rec_mr_update
        partner = mr.partner_id
        postal = partner.postal_coordinate_id
        fix = partner.fix_coordinate_id

        # change some properties
        vals = {
            'phone': '444719',
            'number': '007',
            'box': 'jb',
            'amount': 7.0,
            'reference': '+++555/2017/00055+++',
            'nationality_id': congo,
        }
        vals.update(self.mro.onchange_other_address_componants(
            cr, uid, False,
            mr.country_id.id, mr.address_local_zip_id.id,
            mr.zip_man, mr.town_man,
            mr.address_local_street_id.id, mr.street_man,
            vals['number'], vals['box'])['value'])
        vals.update(self.mro.onchange_technical_name(
            cr, uid, False,
            vals['technical_name'])['value'])
        vals.update(self.mro.onchange_phone(
            cr, uid, False,
            vals['phone'])['value'])

        # update the membership request
        self.mro.write(cr, uid, [mr.id], vals)
        # validate the membership request
        self.mro.validate_request(cr, uid, [mr.id])

        self.assertEqual(mr.firstname, partner.firstname)
        self.assertEqual(mr.email, partner.email_coordinate_id.email,)
        self.assertEqual(mr.mobile, partner.mobile_coordinate_id.phone_id.name)
        self.assertTrue(partner.birth_date)
        self.assertEqual(
            mr.force_int_instance_id.id, partner.int_instance_id.id)
        self.assertFalse(postal.active)
        self.assertFalse(fix.active)
        self.assertEqual(mr.reference, partner.reference)
        self.assertEqual(mr.amount, partner.amount)
        self.assertEqual(mr.nationality_id, partner.nationality_id)

        # 2. partner to create
        mr = self.rec_mr_create
        self.mro.validate_request(cr, uid, [mr.id])

        created_partner_ids = partner_obj.search(
            cr, uid, [('firstname', '=', mr.firstname),
                      ('lastname', '=', mr.lastname),
                      ('birth_date', '=', mr.birth_date), ])
        self.assertEqual(len(created_partner_ids), 1)
        # test address and phone
        address_ids = self.registry['address.address'].search(
            cr, uid, [('technical_name', '=', mr.technical_name)])
        phone_ids = self.registry['phone.phone'].search(
            cr, uid, [('name', '=', mr.phone), ('type', '=', 'fix')])
        self.assertEqual(len(address_ids), 1)
        self.assertEqual(len(phone_ids), 1)

        # test phone.coordinate
        phone_coordinate_ids = self.registry['phone.coordinate'].search(
            cr, uid, [('partner_id', '=', mr.partner_id.id),
                      ('phone_id', '=', phone_ids[0])])
        self.assertEqual(len(phone_coordinate_ids), 1)

    def test_state_default_get(self):
        """
        Test the default state of `membership.state`
        'without_membership' is used as technical state

        Test default state with another default_state
        """
        mrs, cr, uid, context = self.mrs, self.cr, self.uid, {}

        without_membership_id = mrs._state_default_get(
            cr, uid, context=context)
        uniq_code_membership = mrs.browse(
            cr, uid, without_membership_id, context=context)
        self.assertEqual('without_membership', uniq_code_membership.code,
                         "Code should be without_membership")

        code = '%s' % uuid4()
        mrs.create(
            cr, uid, {'name': 'test_state', 'code': code}, context=context)
        uniq_code_membership_id = mrs._state_default_get(
            cr, uid, default_state=code, context=context)
        uniq_code_membership = mrs.browse(cr, uid, uniq_code_membership_id,
                                          context=context)
        self.assertEqual(code, uniq_code_membership.code,
                         "Code should be %s" % code)

    def test_track_changes(self):
        '''
            Test to valid tracks changes method to detect differences
            between modification request and partner data
        '''
        cr, uid = self.cr, self.uid

        request = self.rec_mr_update
        request.write({
            'regional_voluntary': True,
            'local_only': True,
        })

        def get_changes():
            changes = {}
            for change in request.change_ids:
                changes[change.field_name] = (change.old_value,
                                              change.new_value)
            return changes

        changes = get_changes()
        self.assertIn('Firstname', changes)
        self.assertIn('Mobile', changes)
        self.assertIn('Gender', changes)
        self.assertIn('Email', changes)
        self.assertNotIn('Birth Date', changes)
        self.assertIn('Regional voluntary', changes)

        self.assertEqual(changes['Firstname'][0], 'Pauline')
        self.assertEqual(changes['Firstname'][1], 'Paulinne')
        self.assertFalse(changes['Mobile'][0])
        self.assertEqual(changes['Mobile'][1], '+32 475 45 12 32')
        self.assertFalse(changes['Gender'][0])
        self.assertEqual(changes['Gender'][1], 'Female')
        self.assertFalse(changes['Email'][0])
        self.assertEqual(changes['Email'][1], 'pauline_marois@gmail.com')
        self.assertEqual(changes['Regional voluntary'][0], 'No')
        self.assertEqual(changes['Regional voluntary'][1], 'Yes')
        self.assertEqual(changes['Local only'][0], 'No')
        self.assertEqual(changes['Local only'][1], 'Yes')

        # change main address of the partner
        vals = {
            'country_id': self.ref("base.be"),
            'zip_man': '4000',
            'town_man': u'Liège',
            'street_man': 'Place St Lambert',
            'number': '7',
        }
        adr_id = self.registry['address.address'].create(cr, uid, vals)
        vals = {
            'partner_id': request.partner_id.id,
            'address_id': adr_id,
            'is_main': True,
        }
        self.registry['postal.coordinate'].create(cr, uid, vals)

        self.mro.write(cr, uid, request.id, {'lastname': 'Test'})
        changes = get_changes()
        self.assertIn('Name', changes)
        self.assertIn('City', changes)
        self.assertIn('Reference Street', changes)
        self.assertIn('Number', changes)
        self.assertEqual(changes['Name'][0], 'MAROIS')
        self.assertEqual(changes['Name'][1], 'Test')
        self.assertEqual(changes['City'][0], u'Liège')
        self.assertEqual(changes['City'][1], 'Oreye')
        self.assertEqual(changes['Reference Street'][0], 'Place St Lambert')
        self.assertEqual(
            changes['Reference Street'][1], u'Rue Louis Maréchal')
        self.assertEqual(changes['Number'][0], '7')
        self.assertEqual(changes['Number'][1], '6')

        # change address components of the request
        vals = {
            'country_id': self.ref('base.ma'),
            'zip_man': '45000',
            'town_man': 'Ouarzazate',
            'street_man': 'rue du souk',
            'number': '47',
            'box': False,
        }
        vals.update(
            self.mro.onchange_country_id(
                cr, uid, [],
                vals['country_id'], vals['zip_man'], vals['town_man'],
                vals['street_man'], vals['number'], vals['box'])['value']
        )
        vals.update(
            self.mro.onchange_local_zip_id(
                cr, uid, [],
                vals['country_id'], vals['address_local_zip_id'],
                vals['zip_man'], vals['town_man'],
                vals['street_man'], vals['number'], vals['box'])['value']
        )
        vals.update(
            self.mro.onchange_other_address_componants(
                cr, uid, [],
                vals['country_id'], vals['address_local_zip_id'],
                vals['zip_man'], vals['town_man'],
                vals['address_local_street_id'],
                vals['street_man'], vals['number'], vals['box'])['value']
        )
        vals.update(
            self.mro.onchange_technical_name(
                cr, uid, [], vals['technical_name'])['value']
        )
        self.mro.write(cr, uid, request.id, vals)
        changes = get_changes()
        self.assertIn('Country', changes)
        self.assertIn('Zip', changes)
        self.assertIn('Town', changes)
        self.assertIn('Street', changes)
        self.assertIn('Number', changes)
        self.assertEqual(changes['Country'][0], 'Belgium')
        self.assertEqual(changes['Country'][1], 'Morocco')
        self.assertEqual(changes['Zip'][0], '4000')
        self.assertEqual(changes['Zip'][1], '45000')
        self.assertEqual(changes['Town'][0], u'Liège')
        self.assertEqual(changes['Town'][1], 'Ouarzazate')
        self.assertEqual(changes['Street'][0], 'Place St Lambert')
        self.assertEqual(changes['Street'][1], 'rue du souk')
        self.assertEqual(changes['Number'][0], '7')
        self.assertEqual(changes['Number'][1], '47')

        # reset country on request
        self.mro.write(cr, uid, request.id, {'country_id': False})
        changes = get_changes()
        self.assertNotIn('City', changes)
        self.assertNotIn('Zip', changes)
        self.assertNotIn('Town', changes)
        self.assertNotIn('Reference Street', changes)
        self.assertNotIn('Street', changes)
        self.assertNotIn('Street2', changes)
        self.assertNotIn('Number', changes)
        self.assertNotIn('Box', changes)
        self.assertNotIn('Sequence', changes)

    def test_age_computation(self):
        """
        Check value of age depending of the birth_date
        """
        cr, uid, context = self.cr, self.uid, {}
        age = 10
        birth_date = datetime.strftime(
            date.today() - relativedelta(years=age),
            DEFAULT_SERVER_DATE_FORMAT)
        vals = {
            'birth_date': birth_date,
        }
        mr_id = self.ref('%s.membership_request_mp' % self._module_ns)
        clone_id = self.mro.copy(cr, uid, mr_id, context=context)
        mr = self.mro.browse(cr, uid, clone_id, context=context)
        self.mro.write(cr, uid, [mr.id], vals, context=context)
        mr = self.mro.browse(cr, uid, mr.id, context=context)
        self.assertEqual(mr.age, age, 'Should be the same age')

    def test_required_age(self):
        mr_obj = self.env['membership.request']
        minage = int(self.env['ir.config_parameter'].get_param(
            MR_REQUIRED_AGE_KEY, default=16))
        name = 'Test'
        d = date.today() - relativedelta(years=minage) + relativedelta(days=1)
        vals = {
            'lastname': name,
            'firstname': name,
            'state': 'confirm',
            'gender': 'm',
            'day': d.day,
            'month': d.month,
            'year': d.year,
            'request_type': 'm',
        }
        mr = mr_obj.with_context(mode='ws').create(vals)
        self.assertRaises(ValidationError, mr.validate_request)

        d = date.today() - relativedelta(years=minage)
        vals = {
            'day': d.day,
            'month': d.month,
            'year': d.year,
        }
        oc = mr.onchange_partner_component(
            False, d.day, d.month, d.year, name, name, None, False)
        vals['birth_date'] = oc['value'].get('birth_date', False)
        mr.write(vals)
        mr.validate_request()
        self.assertEqual(mr.state, 'validate', 'Validation should work')

    def test_phone_auto_change_type(self):
        '''
            Use case tested:
            ----------------
            - Jacques has the number +32 473 78 10 80 set as mobile in the
              database.
            - A membership request is created with +32 473 78 10 80 set as a
              fix phone number.
            ==> The validation of the request should automatically change the
                phone number as fix in the database and fix all linked
                coordinates as main
        '''
        mr_obj = self.env['membership.request']
        vals = {
            'lastname': 'LE CROQUANT',
            'firstname': 'Jacques',
            'state': 'confirm',
            'request_type': 'm',
            'phone': self.mobile_five.name,
            'partner_id': self.rec_partner_jacques.id
        }
        vals = mr_obj._pre_process(vals)
        mr1 = mr_obj.create(vals)
        mr1.validate_request()
        self.env.invalidate_all()
        self.assertEqual(self.mobile_five.type, 'fix')
        self.assertEqual(self.coord_mobile_2.coordinate_type, 'fix')
        self.assertTrue(self.coord_mobile_2.is_main)
