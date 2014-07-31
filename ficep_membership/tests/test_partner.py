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
from anybox.testing.openerp import SharedSetupTransactionCase
import uuid
from openerp import netsvc
from datetime import date, timedelta
import logging
from openerp.addons.ficep_membership import membership_request


wf_service = netsvc.LocalService("workflow")
_logger = logging.getLogger(__name__)


class test_partner(SharedSetupTransactionCase):

    _data_files = (
        # load the partner
        '../../ficep_base/tests/data/res_partner_data.xml',
        # load the birth_date of this partner
        '../../ficep_person/tests/data/res_partner_data.xml',
        # load address of this partner
        '../../ficep_structure/tests/data/structure_data.xml',
        '../../ficep_address/tests/data/reference_data.xml',
        # load postal_coordinate of this partner
        '../../ficep_address/tests/data/address_data.xml',
        # load phone_coordinate of this partner
        '../../ficep_phone/tests/data/phone_data.xml',
        # load phone_coordinate of this partner
        '../../ficep_thesaurus/tests/data/thesaurus_data.xml',
    )

    _module_ns = 'ficep_membership'

    def setUp(self):
        super(test_partner, self).setUp()

        self.mr_obj = self.registry('membership.request')
        membership_request._set_disable_rollback_for_test(True)

        self.partner_obj = self.registry('res.partner')
        self.ms_obj = self.registry('membership.state')
        self.ml_obj = self.registry('membership.membership_line')

        self.rec_partner = self.browse_ref('%s.res_partner_thierry' % self._module_ns)

    def get_partner(self, partner_id=False):
        """
        ==========
        get_partner
        ==========
        return a new browse record of partner
        """
        if not partner_id:
            name = uuid.uuid4()
            partner_values = {
                'name': name,
            }
            partner_id = self.partner_obj.create(self.cr, self.uid, partner_values)
        # check each tume the current state cs
        return self.partner_obj.browse(self.cr, self.uid, partner_id)

    def test_workflow(self):
        """
        =============
        test_workflow
        =============
        Test all possible ways of partner membership workflow
        Check `state_membership_id`:
        * create = without_membership
        * without_status -> candidate_member
        * without_status -> supporter -> candidate_member
            -> future_commitee_member -> refused_candidate_member
            -> supporter -> future_commitee_member -> refused_candidate_member
            -> candidate_member -> supporter -> old_supporter
        * without_status -> candidate_member -> future_commitee_member
            -> member -> old_member -> old_commitee_member -> member
            -> old_member -> old_commitee_member -> inappropriate_old_member
        * old_member -> inappropriate_old_member
        * old_member -> break_old_member
        * member -> expulsion_old_member
        * member -> resignation_old_member
        """
        cr, uid, partner_obj = self.cr, self.uid, self.partner_obj

        # create = without_membership
        partner = self.get_partner()
        self.assertEquals(partner.membership_state_id.code, 'without_membership', 'Create: should be "without_status"')

        # without_status -> candidate_member
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'candidate_member', 'Should be "candidate_member"')

        # without_status -> supporter
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': True})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'supporter', 'Should be "supporter"')

        # supporter -> candidate_member
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'candidate_member', 'Should be "candidate_member"')

        # candidate_member -> future_commitee_member
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'future_commitee_member', 'Should be "future_commitee_member"')

        # future_commitee_member -> refused_candidate_member
        partner.write({'rejected_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'refused_candidate_member', 'Should be "refused_candidate_member"')

        # refused candidate_member -> candidate_member
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'candidate_member', 'Should be "candidate_member"')

        # candidate_member ->supporter
        partner.write({'decline_payment_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': True})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'supporter', 'Should be "supporter"')

        # supporter -> old_supporter
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_supporter', 'Should be "old_supporter"')

        # go to member state
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'accept', self.cr)
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'member', 'Should be "member"')

        # member -> old_member
        partner.write({'decline_payment_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_member', 'Should be "old member"')

        # old_member -> old_commitee_member
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_commitee_member', 'Should be "old_commitee_member"')

        # old_commitee_member -> inappropriate_old_member
        partner.write({'exclusion_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'inappropriate_old_member', 'Should be "inappropriate_old_member"')

        # Go to member
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'accept', self.cr)
        partner = self.get_partner(partner.id)

        # member -> resignation_old_member
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'resignation_old_member', 'Should be "resignation_old_member"')

        # Go to member
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'accept', self.cr)
        partner = self.get_partner(partner.id)

        # member -> expulsion_old_member
        partner.write({'exclusion_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'expulsion_old_member', 'Should be "expulsion_old_member"')

        # Go to old commitee member
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'accept', self.cr)
        partner = self.get_partner(partner.id)

        # member -> old_member
        partner.write({'decline_payment_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_member', 'Should be "old member"')

        # old_member -> old_commitee_member
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_commitee_member', 'Should be "old_commitee_member"')

        # old_commitee_member -> break_old_member
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)

        # go to old member
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'accept', self.cr)
        partner = self.get_partner(partner.id)

        # member -> resignation_old_member
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'resignation_old_member', 'Should be "break_old_member"')

    def test_button_modification_request(self):
        """
        ====================
        modification_request
        ====================
        Check that a `membership.request` object is well created with
        the datas of the giving partner.
        test raise if partner does not exist
        """
        mr_obj, partner, cr, uid, context = self.mr_obj, self.rec_partner, self.cr, self.uid, {}
        res = self.partner_obj.button_modification_request(cr, uid, [partner.id], context=context)
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
        self.assertEqual(mr.membership_state_id, partner.membership_state_id, '[memb.req.]membership_state_id should be the same that [partner]membership_state_id ')
        self.assertEqual(mr.identifier, partner.identifier, '[memb.req.]identifier should be the same that [partner]identifier ')
        self.assertEqual(mr.lastname, partner.lastname, '[memb.req.]lastname should be the same that [partner]lastname ')
        self.assertEqual(mr.firstname, partner.firstname, '[memb.req.]firstname should be the same that [partner]firstname ')
        self.assertEqual(mr.gender, partner.gender, '[memb.req.]gender should be the same that [partner]gender ')
        self.assertEqual(mr.birth_date, birth_date, '[memb.req.]birth_date should be the same that [partner]birth_date ')
        self.assertEqual(mr.day, day and int(day), '[memb.req.]day should be the same that [partner]day ')
        self.assertEqual(mr.month, month and int(month), '[memb.req.]month should be the same that [partner]month ')
        self.assertEqual(mr.year, year and int(year), '[memb.req.]year should be the same that [partner]year ')
        self.assertEqual(mr.is_update, True, '[memb.req.]is_update should be True')
        self.assertEqual(mr.country_id and mr.country_id.id or False, postal_coordinate_id and postal_coordinate_id.address_id.country_id.id, \
                         '[memb.req.]country_id should be the same that [partner]country_id ')
        self.assertEqual(mr.address_local_street_id and mr.address_local_street_id.id or False, postal_coordinate_id and postal_coordinate_id.address_id.address_local_street_id.id, \
                         '[memb.req.]address_local_street_id should be the same that [partner]address_local_street_id ')
        self.assertEqual(mr.street_man, postal_coordinate_id and postal_coordinate_id.address_id.street_man, \
                         '[memb.req.]street_man should be the same that [partner]street_man ')
        self.assertEqual(mr.street2, postal_coordinate_id and postal_coordinate_id.address_id.street2, \
                         '[memb.req.]street2 should be the same that [partner]street2 ')
        self.assertEqual(mr.address_local_zip_id and mr.address_local_zip_id.id or False, postal_coordinate_id and postal_coordinate_id.address_id.address_local_zip_id.id, \
                         '[memb.req.]address_local_zip_id should be the same that [partner]address_local_zip_id ')
        self.assertEqual(mr.zip_man, postal_coordinate_id and postal_coordinate_id.address_id.zip_man, \
                         '[memb.req.]zip_man should be the same that [partner]zip_man ')
        self.assertEqual(mr.town_man, postal_coordinate_id and postal_coordinate_id.address_id.town_man, \
                         '[memb.req.]town_man should be the same that [partner]town_man ')
        self.assertEqual(mr.box, postal_coordinate_id and postal_coordinate_id.address_id.box, \
                         '[memb.req.]box should be the same that [partner]box ')
        self.assertEqual(mr.number, postal_coordinate_id and postal_coordinate_id.address_id.number, \
                         '[memb.req.]number should be the same that [partner]number ')
        self.assertEqual(mr.mobile, mobile_coordinate_id and mobile_coordinate_id.phone_id.name, \
                         '[memb.req.]mobile should be the same that [partner]mobile ')
        self.assertEqual(mr.phone, fix_coordinate_id and fix_coordinate_id.phone_id.name, \
                         '[memb.req.]phone should be the same that [partner]phone ')
        self.assertEqual(mr.mobile_id and mr.mobile_id.id or False, mobile_coordinate_id and mobile_coordinate_id.phone_id.id, \
                         '[memb.req.]mobile_id should be the same that [partner]mobile_id ')
        self.assertEqual(mr.phone_id and mr.phone_id.id or False, fix_coordinate_id and fix_coordinate_id.phone_id.id, \
                         '[memb.req.]phone_id should be the same that [partner]phone_id ')
        self.assertEqual(mr.email, email_coordinate_id and email_coordinate_id.email, \
                         '[memb.req.]email should be the same that [partner]email ')
        self.assertEqual(mr.address_id and mr.address_id.id or False, postal_coordinate_id and postal_coordinate_id.address_id.id, \
                         '[memb.req.]address_id should be the same that [partner]address_id ')
        self.assertEqual(mr.int_instance_id and mr.int_instance_id.id or False, int_instance_id and int_instance_id.id, \
                         '[memb.req.]int_instance_id should be the same that [partner]int_instance_id ')
        self.assertEqual(mr.interests_m2m_ids or [[6, False, []]], [[6, False, partner.interests_m2m_ids and [interest.id for interest in partner.interests_m2m_ids] or []]], \
                         '[memb.req.]interests_m2m_ids should be the same that [partner]interests_m2m_ids ')
        self.assertEqual(mr.partner_id and mr.partner_id.id, partner.id, '[memb.req.]partner_id should be the same that [partner]partner_id ')
        self.assertEqual(mr.competencies_m2m_ids or [[6, False, []]], [[6, False, partner.competencies_m2m_ids and [competence.id for competence in partner.competencies_m2m_ids] or []]], \
                         '[memb.req.]competencies_m2m_ids should be the same that [partner]competencies_m2m_ids ')

    def test_update_membership_line(self):
        """
        ======================
        update_membership_line
        ======================
        Check that calling this method will first create a membership_line
        for a giving partner and then call it a second time to check that an update is
        made for the first membership line and a new creation
        Process One:
            * date from = today
            * membership_state = partner status
            * date_to = False
            * is_current = True
        Process two:
            * update first:
                 * date_to = today
                 * is_current = False
            * new_one:
                 * date from = today
                 * membership_state = partner status
                 * date_to = False
                 * is_current = True
        change status of the partner: this action will automatically launch `update_membership_line`
        and then the second process will be executed
        """
        ml_obj, partner, partner_obj, cr, uid, context = self.ml_obj, self.rec_partner, self.partner_obj, self.cr, self.uid, {}
        partner_obj.update_membership_line(cr, uid, [partner.id], context=context)
        partner = partner_obj.browse(cr, uid, partner.id, context=context)
        today = date.today().strftime('%Y-%m-%d')
        membership_state_id = partner.membership_state_id and partner.membership_state_id.id or False

        for membership_line in partner.member_lines:
            self.assertEqual(membership_line.date_from, today, 'Date From should be: today')
            self.assertEqual(membership_line.membership_state_id.id, membership_state_id, \
                             'State of membership must be the same that state of partner')
            self.assertTrue(membership_line.is_current, 'First membership should be the current one')
            self.assertFalse(membership_line.date_to, 'Should not have a date_to because this is the current membership')

        partner.write({'accepted_date': today})
        partner = partner_obj.browse(cr, uid, partner.id, context=context)
        self.assertTrue(len(partner.member_lines) == 2, "Sould have two member lines: one for the previous first call and another\
                                                            for the current update of status")
        one_current = False
        for membership_line in partner.member_lines:
            if membership_line.is_current == True:
                one_current = True
                self.assertTrue(membership_line.membership_state_id == partner.membership_state_id, \
                                 'State Should be the same than partner')
            else:
                self.assertTrue(membership_line.membership_state_id.id == membership_state_id, \
                                 'State Should be the same than before')
                self.assertTrue(membership_line.date_to, '`date_to` should has been set')
        self.assertTrue(one_current, 'Should at least have one current')

    def test_waiting_member(self):
        """
        ===================
        test_waiting_member
        ===================
        Test will identify member with the status
        `future_commitee_member` and `old_commitee_member`
        and make them pass into `member` status only if they are
        into the previous state for (or more than) one month
        """
        cr, uid, context = self.cr, self.uid, {}
        wmr = self.registry['waiting.member.report']
        vals = {
            'lastname': '%s' % uuid.uuid4()
        }
        partner_id = self.partner_obj.create(cr, uid, vals, context=context)
        # futur commitee member less than one month
        partner = self.partner_obj.browse(cr, uid, partner_id, context=context)

        partner.write({
            'accepted_date': date.today().strftime('%Y-%m-%d'),
            'free_member': False
        })
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'paid_simulated', self.cr)

        partner = self.partner_obj.browse(cr, uid, partner_id, context=context)
        current_state = partner.membership_state_id
        # now into future commitee member
        wmr.process_accept_members(cr, uid)
        partner = self.partner_obj.browse(cr, uid, partner_id, context=context)

        self.assertEqual(partner.membership_state_id, current_state, "State Should be the same than before")

        for member_line in partner.member_lines:
            if member_line.is_current:
                member_line.write({'date_from': '%s' % (date.today() -\
                    timedelta(days=31)).strftime('%Y-%m-%d')})

        wmr.process_accept_members(cr, uid)
        partner = self.partner_obj.browse(cr, uid, partner_id, context=context)

        self.assertNotEqual(partner.membership_state_id, current_state, "State Should not be the same than before")
        self.assertEqual(partner.membership_state_id.code, 'member', "State Should be 'member'")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
