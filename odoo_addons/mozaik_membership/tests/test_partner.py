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

from datetime import date
from anybox.testing.openerp import SharedSetupTransactionCase
import uuid

from openerp.osv import orm


class test_partner(SharedSetupTransactionCase):

    _data_files = (
        # load the partner
        '../../mozaik_base/tests/data/res_partner_data.xml',
        # load structures
        '../../mozaik_structure/tests/data/structure_data.xml',
        '../../mozaik_address/tests/data/reference_data.xml',
        '../../mozaik_address/tests/data/address_data.xml',
    )

    _module_ns = 'mozaik_membership'

    def setUp(self):
        super(test_partner, self).setUp()

        self.mr_obj = self.registry('membership.request')
        self.partner_obj = self.registry('res.partner')
        self.ms_obj = self.registry('membership.state')
        self.ml_obj = self.registry('membership.line')
        self.prd_obj = self.registry('product.template')
        self.imd_obj = self.registry['ir.model.data']

        self.partner1 = self.browse_ref(
            '%s.res_partner_thierry' % self._module_ns)

        self.partner2 = self.browse_ref(
            '%s.res_partner_fgtb' % self._module_ns)

        self.user_model = self.registry('res.users')
        self.partner_jacques_id = self.ref(
            '%s.res_partner_jacques' % self._module_ns)
        self.group_fr_id = self.ref('mozaik_base.mozaik_res_groups_reader')

    def get_partner(self, partner_id=False):
        """
        Return a new browse record of partner
        """
        if not partner_id:
            name = uuid.uuid4()
            partner_values = {
                'lastname': name,
            }
            partner_id = self.partner_obj.create(self.cr, self.uid,
                                                 partner_values)
        # check each time the current state change
        return self.partner_obj.browse(self.cr, self.uid, partner_id)

    def test_workflow(self):
        """
        Test all possible ways of partner membership workflow
        Check `state_membership_id`:
        * create = without_membership
        * without_status -> member_candidate
        * without_status -> supporter -> member_candidate
            -> member_committee -> refused_member_candidate
            -> supporter -> member_committee -> refused_member_candidate
            -> member_candidate -> supporter -> former_supporter -> supporter
        * without_status -> member_candidate -> member_committee
            -> member -> former_member -> former_member_committee -> member
            -> former_member -> former_member_committee
                -> inappropriate_former_member
        * former_member -> inappropriate_former_member -> former_member
        * former_member -> break_former_member -> former_member
        * member -> expulsion_former_member -> former_member
        * member -> resignation_former_member -> former_member
        """
        cr, uid = self.cr, self.uid
        partner_obj = self.partner_obj
        prd_obj = self.prd_obj
        imd_obj = self.imd_obj
        today = date.today().strftime('%Y-%m-%d')

        # create = without_membership
        partner = self.get_partner()
        self.assertEquals(partner.membership_state_id.code,
                          'without_membership',
                          'Create: should be "without_status"')

        # without_status -> member_candidate
        partner.write({'accepted_date': today, 'free_member': False})
        self.assertEquals(partner.membership_state_id.code,
                          'member_candidate', 'Should be "member_candidate"')

        nbl = 0

        # without_status -> supporter
        partner = self.get_partner()
        partner.write({
            'accepted_date': today, 'free_member': True,
            'del_doc_date': today,
        })
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'supporter',
                          'Should be "supporter"')

        # supporter -> former_supporter
        partner_obj.resign(cr, uid, [partner.id])
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'former_supporter', 'Should be "former_supporter"')
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'supporter', 'Should be "supporter"')

        # supporter -> member_candidate
        partner.write({'accepted_date': today, 'free_member': False})
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'member_candidate', 'Should be "member_candidate"')
        self.assertFalse(partner.del_doc_date)

        # member_candidate -> supporter
        partner.write({'decline_payment_date': today, 'free_member': True})
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'supporter',
                          'Should be "supporter"')

        # supporter -> member_candidate (already tested)
        partner.write({'accepted_date': today, 'free_member': False})
        nbl += 1

        # member_candidate -> refused_member_candidate
        partner.write({'rejected_date': today})
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'refused_member_candidate',
                          'Should be "refused_member_candidate"')

        # refused_member_candidate -> member_candidate
        partner.write({'accepted_date': today, 'free_member': False})
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'member_candidate',
                          'Should be "member_candidate"')

        # member_candidate -> member_committee
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'member_committee',
                          'Should be "member_committee"')

        # member_committee -> refused_member_candidate
        partner.write({'rejected_date': today})
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'refused_member_candidate',
                          'Should be "refused_member_candidate"')

        # refused_member_candidate -> supporter
        partner.write({'accepted_date': today, 'free_member': True})
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'supporter',
                          'Should be "supporter"')

        # supporter -> member_committee
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'member_committee',
                          'Should be "member_committee"')

        # member_committee -> member
        partner_obj.signal_workflow(cr, uid, [partner.id], 'accept')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'member',
                          'Should be "member"')

        # member -> former_member
        partner.write({'decline_payment_date': today})
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'former_member',
                          'Should be "former_member"')

        # former_member -> former_member_committee
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'former_member_committee',
                          'Should be "former_member_committee"')

        # former_member_committee -> inappropriate_former_member
        partner_obj.exclude(cr, uid, [partner.id])
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'inappropriate_former_member',
                          'Should be "inappropriate_former_member"')

        # inappropriate_former_member -> former_member
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'former_member',
                          'Should be "former_member"')

        # former_member -> inappropriate_former_member
        partner_obj.exclude(cr, uid, [partner.id])
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'inappropriate_former_member',
                          'Should be "inappropriate_former_member"')

        # inappropriate_former_member -> former_member (already tested)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1

        # former_member -> break_former_member
        partner_obj.resign(cr, uid, [partner.id])
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'break_former_member',
                          'Should be "break_former_member"')

        # break_former_member -> former_member
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'former_member',
                          'Should be "former_member"')

        # former_member -> former_member_committee (already tested)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1

        # former_member_committee -> member
        partner_obj.signal_workflow(cr, uid, [partner.id], 'accept')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'member',
                          'Should be "member"')

        # member -> resignation_former_member
        partner_obj.resign(cr, uid, [partner.id])
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'resignation_former_member',
                          'Should be "resignation_former_member"')
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'former_member',
                          'Should be "former_member"')

        # former_member -> former_member_committee -> member (already tested)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'paid')
        nbl += 1
        ml = partner_obj._get_active_membership_line(cr, uid, partner.id)
        def_prd_id = prd_obj._get_default_subscription(cr, uid)
        ml.write({
            'product_id': def_prd_id,
            'price': 44.44,
        })
        self.assertEquals(partner.subscription_product_id.id,
                          def_prd_id,
                          'Should be "Usual Subscription" (id=%s)' %
                          def_prd_id)
        partner_obj.signal_workflow(cr, uid, [partner.id], 'accept')
        nbl += 1

        # member -> member (with free subscription)
        partner_obj.register_free_membership(cr, uid, [partner.id])
        nbl += 1
        self.assertEquals(partner.membership_state_id.code, 'member',
                          'Should be "member"')
        ml = partner_obj._get_active_membership_line(cr, uid, partner.id)
        self.assertEquals(ml.price, 0.0, 'Should be "0.0')
        free_prd_id = imd_obj.xmlid_to_res_id(
            cr, uid, 'mozaik_membership.membership_product_free')
        self.assertEquals(partner.subscription_product_id.id,
                          free_prd_id,
                          'Should be "Free Subscription" (id=%s)' %
                          free_prd_id)

        # member -> expulsion_former_member
        partner_obj.exclude(cr, uid, [partner.id])
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'expulsion_former_member',
                          'Should be "expulsion_former_member"')
        partner_obj.signal_workflow(cr, uid, [partner.id], 'reset')
        nbl += 1
        self.assertEquals(partner.membership_state_id.code,
                          'former_member',
                          'Should be "former_member"')

        # number of membership lines ?
        self.assertEquals(len(partner.membership_line_ids),
                          nbl,
                          'Should be "%s"' % nbl)

    def test_button_modification_request(self):
        """
        Check that a `membership.request` object is well created with
        the datas of the giving partner.
        test raise if partner does not exist
        """
        mr_obj, partner, cr, uid, context = self.mr_obj,\
            self.partner1, self.cr, self.uid, {}
        res = self.partner_obj.button_modification_request(cr, uid,
                                                           [partner.id],
                                                           context=context)
        mr = mr_obj.browse(cr, uid, res['res_id'], context=context)
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
        self.assertEqual(mr.membership_state_id, partner.membership_state_id)
        self.assertEqual(mr.result_type_id, partner.membership_state_id)
        self.assertEqual(mr.identifier, partner.identifier, '[memb.req.]\
        identifier should be the same that [partner]identifier ')
        self.assertEqual(mr.lastname, partner.lastname, '[memb.req.]lastname\
        should be the same that [partner]lastname ')
        self.assertEqual(mr.firstname, partner.firstname, '[memb.req.]\
        firstname should be the same that [partner]firstname ')
        self.assertEqual(mr.gender, partner.gender, '[memb.req.]gender should \
        be the same that [partner]gender ')
        self.assertEqual(mr.birth_date, birth_date, '[memb.req.]birth_date \
        should be the same that [partner]birth_date ')
        self.assertEqual(mr.day, day and int(day), '[memb.req.]day should be \
        the same that [partner]day ')
        self.assertEqual(mr.month, month and int(month), '[memb.req.]month \
        should be the same that [partner]month ')
        self.assertEqual(mr.year, year and int(year), '[memb.req.]year should\
        be the same that [partner]year ')
        self.assertEqual(mr.is_update, True, '[memb.req.]is_update should be \
        True')
        self.assertEqual(mr.country_id and mr.country_id.id or False,
                         postal_coordinate_id and postal_coordinate_id.
                         address_id.country_id.id, '[memb.req.]country_id \
                         should be the same that [partner]country_id ')
        self.assertEqual(mr.address_local_street_id and
                         mr.address_local_street_id.id or False,
                         postal_coordinate_id and postal_coordinate_id.
                         address_id.address_local_street_id.id,
                         '[memb.req.]address_local_street_id should be the \
                         same that [partner]address_local_street_id ')
        self.assertEqual(mr.street_man, postal_coordinate_id and
                         postal_coordinate_id.address_id.street_man,
                         '[memb.req.]street_man should be the same that\
                         [partner]street_man ')
        self.assertEqual(mr.street2, postal_coordinate_id and
                         postal_coordinate_id.address_id.street2,
                         '[memb.req.]street2 should be the same that \
                         [partner]street2 ')
        self.assertEqual(mr.address_local_zip_id and
                         mr.address_local_zip_id.id or False,
                         postal_coordinate_id and postal_coordinate_id.
                         address_id.address_local_zip_id.id,
                         '[memb.req.]address_local_zip_id should be the same\
                         that [partner]address_local_zip_id ')
        self.assertEqual(mr.zip_man, postal_coordinate_id and
                         postal_coordinate_id.address_id.zip_man,
                         '[memb.req.]zip_man should be the same that \
                         [partner]zip_man')
        self.assertEqual(mr.town_man, postal_coordinate_id and
                         postal_coordinate_id.address_id.town_man,
                         '[memb.req.]town_man should be the same that \
                         [partner]town_man')
        self.assertEqual(mr.box, postal_coordinate_id and
                         postal_coordinate_id.address_id.box,
                         '[memb.req.]box should be the same that [partner]box')
        self.assertEqual(mr.number, postal_coordinate_id and
                         postal_coordinate_id.address_id.number,
                         '[memb.req.]number should be the same that \
                         [partner]number')
        self.assertEqual(mr.mobile, mobile_coordinate_id and
                         mobile_coordinate_id.phone_id.name,
                         '[memb.req.]mobile should be the same that \
                         [partner]mobile')
        self.assertEqual(mr.phone, fix_coordinate_id and
                         fix_coordinate_id.phone_id.name,
                         '[memb.req.]phone should be the same that \
                         [partner]phone')
        self.assertEqual(mr.mobile_id and mr.mobile_id.id or False,
                         mobile_coordinate_id and mobile_coordinate_id.
                         phone_id.id, '[memb.req.]mobile_id should be the \
                         same that [partner]mobile_id ')
        self.assertEqual(mr.phone_id and mr.phone_id.id or False,
                         fix_coordinate_id and fix_coordinate_id.phone_id.id,
                         '[memb.req.]phone_id should be the same that \
                         [partner]phone_id')
        self.assertEqual(mr.email, email_coordinate_id and
                         email_coordinate_id.email, '[memb.req.]email should \
                         be the same that [partner]email')
        self.assertEqual(mr.address_id and mr.address_id.id or False,
                         postal_coordinate_id and
                         postal_coordinate_id.address_id.id,
                         '[memb.req.]address_id should be the same that \
                         [partner]address_id ')
        self.assertEqual(mr.int_instance_id and mr.int_instance_id.id or
                         False, int_instance_id and int_instance_id.id,
                         '[memb.req.]int_instance_id should be the same that \
                         [partner]int_instance_id ')
        self.assertEqual(mr.interests_m2m_ids or [[6, False, []]],
                         [[6, False, partner.interests_m2m_ids and
                           [interest.id for interest in
                            partner.interests_m2m_ids] or []]],
                         '[memb.req.]interests_m2m_ids should be the same \
                         that [partner]interests_m2m_ids ')
        self.assertEqual(mr.partner_id and mr.partner_id.id, partner.id,
                         '[memb.req.]partner_id should be the same that \
                         [partner]partner_id ')
        self.assertEqual(mr.competencies_m2m_ids or [[6, False, []]],
                         [[6, False, partner.competencies_m2m_ids and
                           [competence.id for competence in
                            partner.competencies_m2m_ids] or []]],
                         '[memb.req.]competencies_m2m_ids should be the same \
                         that [partner]competencies_m2m_ids ')

    def test_update_membership_line(self):
        """
        Check that calling this method will first create a membership_line
        for a giving partner and then call it a second time to check that an
        update is made for the first membership line and a new creation
        Process One:
            * date from = today
            * membership_state = partner status
            * date_to = False
            * active = True
        Process two:
            * update first:
                 * date_to = today
                 * active = False
            * new_one:
                 * date from = today
                 * membership_state = partner status
                 * date_to = False
                 * active = True
        change status of the partner: this action will automatically launch
        `update_membership_line`
        and then the second process will be executed
        """
        partner, partner_obj = self.partner1, self.partner_obj
        cr, uid, context = self.cr, self.uid, {'active_test': True}
        partner_obj.update_membership_line(cr, uid, [partner.id],
                                           context=context)
        partner = partner_obj.browse(cr, uid, partner.id, context=context)
        today = date.today().strftime('%Y-%m-%d')
        membership_state_id = partner.membership_state_id and \
            partner.membership_state_id.id or False

        for membership_line in partner.membership_line_ids:
            if membership_line.active:
                self.assertFalse(membership_line.date_to, 'Should not have a \
                    date_to because this is the current membership')
                self.assertEqual(membership_line.membership_state_id.id,
                                 membership_state_id, 'State of membership \
                                 must be the same that state of partner')
            self.assertEqual(membership_line.date_from, today,
                             'Date From should be: today')
        partner.write({'accepted_date': today})
        partner = partner_obj.browse(cr, uid, partner.id, context=context)
        self.assertTrue(len(partner.membership_line_ids) >= 1, "Sould have "
                        "one member lines: previous first call "
                        "(without_membership) should not create lines "
                        "and another for the current update of status")
        one_current = False
        for membership_line in partner.membership_line_ids:
            if membership_line.active:
                one_current = True
                self.assertTrue(membership_line.state_id ==
                                partner.membership_state_id,
                                'State Should be the same than partner')
            else:
                self.assertTrue(membership_line.state_id.id ==
                                membership_state_id,
                                'State Should be the same than before')
                self.assertTrue(membership_line.date_to,
                                '`date_to` should has been set')
        self.assertTrue(one_current, 'Should at least have one current')

    def test_update_is_company(self):
        """
        Check that the existence of a workflow attached to a partner is
        correctly handled regarding the flag is_company:
        1- True: no workflow, state=None
        2- False: with workflow, state!=None
        3- is_company: True=>False: always possible
        4- is_company: False=>True: only possible without membership history
        5- otherwise exception
        """
        cr, uid, context = self.cr, self.uid, {}
        partner, partner_obj = self.partner2, self.partner_obj

        pid = partner.id

        def wkf_exist():
            cr.execute("SELECT 1 "
                       "FROM wkf w, wkf_instance i "
                       "WHERE i.wkf_id = w.id "
                       "AND w.osv = 'res.partner' "
                       "AND i.res_id = %s",
                       (pid,))
            one = cr.fetchone()
            return one

        # 1- True: no workflow, state=None
        self.assertFalse(
            wkf_exist(),
            'No workflow should be existed for a legal person')
        self.assertFalse(
            partner.membership_state_id,
            'Field membership_state_id should be None '
            'because the partner is a company')

        # 2- False: with workflow, state!=None
        # 3- is_company: True => False: always possible
        partner_obj.write(cr, uid, pid, {'is_company': False})
        self.assertTrue(
            wkf_exist(),
            'A workflow should be existed for a natural person')
        self.assertTrue(
            partner.membership_state_id,
            'Field membership_state_id should be initialised '
            'because the partner is not a company')

        # 4- is_company: False=>True: only possible without membership history
        partner_obj.write(cr, uid, pid, {'is_company': True})
        self.assertFalse(
            wkf_exist(),
            'No workflow should be existed for a legal person')
        self.assertFalse(
            partner.membership_state_id,
            'Field membership_state_id should be None '
            'because the partner is a company')

        # 5- otherwise exception
        partner_obj.write(cr, uid, pid, {'is_company': False})
        res = partner_obj.button_modification_request(
            cr, uid, [pid], context=context)
        mr_id = res['res_id']
        imd_obj = self.imd_obj
        vals = {
            'country_id': imd_obj.get_object_reference(
                cr, uid, 'base', 'ad')[1],
            'request_type': 'm',
        }
        self.mr_obj.write(cr, uid, [mr_id], vals)
        # validate the request => a first history line is created
        self.mr_obj.validate_request(cr, uid, [mr_id])
        # a return to a company must failed
        self.assertRaises(
            orm.except_orm,
            partner_obj.write,
            cr, uid, pid, {'is_company': True})
        pass

    def test_change_instance(self):
        '''
        Check that instance well updated into the partner when its main postal
        coo is changed
        '''
        cr, uid, context = self.cr, self.uid, {}
        postal_obj = self.registry['postal.coordinate']
        address_obj = self.registry['address.address']
        zip_obj = self.registry['address.local.zip']

        int_instance_id = self.ref('%s.int_instance_06' % self._module_ns)

        postal_ids = postal_obj.search(cr, uid, [], limit=1, context=context)
        postal_rec = postal_obj.browse(cr, uid, postal_ids, context=context)[0]
        partner_id = postal_rec.partner_id.id
        vals = {
            'local_zip': '123456789',
            'town': 'numbers',
            'int_instance_id': int_instance_id,
        }
        zip_id = zip_obj.create(cr, uid, vals, context=context)
        vals = {
            'country_id': self.ref("base.be"),
            'address_local_zip_id': zip_id,
        }
        address_id = address_obj.create(cr, uid, vals, context=context)
        vals = {
            'address_id': address_id,
            'partner_id': partner_id,
            'is_main': True,
        }
        postal_id = postal_obj.create(cr, uid, vals, context=context)
        postal_rec = postal_obj.browse(cr, uid, postal_id, context=context)
        self.assertEquals(int_instance_id,
                          postal_rec.partner_id.int_instance_id.id,
                          'Instance should be the same')

    def test_generate_membership_reference(self):
        """
        Check if the membership reference match the arbitrary pattern:
          'MS: YYYY/<partner-id>'
        """
        cr, uid, context = self.cr, self.uid, {}
        p_obj = self.partner_obj
        # create a partner
        partner_id = p_obj.create(
            cr, uid, {'lastname': '%s' % uuid.uuid4()}, context=context)
        year = str(date.today().year)
        # generate the reference
        genref = p_obj._generate_membership_reference(
            cr, uid, partner_id, year, context=context)

        ref = 'MS: %s/%s' % (year, partner_id)
        self.assertEquals(genref, ref,
                          'Reference should be equal to %s' % ref)

    def test_create_user_from_partner(self):
        """
        Test the propagation of int_instance into the int_instance_m2m_ids
        when creating a user from a partner
        """
        cr, uid, context = self.cr, self.uid, {}
        jacques_id = self.partner_jacques_id
        fr_id = self.group_fr_id
        partner_model, user_model = self.partner_obj, self.user_model

        # Check for reference data
        dom = [('partner_id', '=', jacques_id)]
        vals = user_model.search(cr, uid, dom, context=context)
        self.assertFalse(
            len(vals), 'Wrong expected reference data for this test')
        dom = [('id', '=', jacques_id), ('ldap_name', '>', '')]
        vals = partner_model.search(cr, uid, dom, context=context)
        self.assertFalse(
            len(vals), 'Wrong expected reference data for this test')

        # Create a user from a partner
        partner_model.create_user(
            cr, uid, 'jack', jacques_id, [fr_id], context=context)
        jack = partner_model.browse(cr, uid, jacques_id, context=context)
        self.assertEqual(
            [jack.int_instance_id.id], jack.int_instance_m2m_ids.ids,
            'Update partner fails with wrong int_instance_m2m_ids')
