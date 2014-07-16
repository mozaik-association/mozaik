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
from datetime import date
import logging


wf_service = netsvc.LocalService("workflow")
_logger = logging.getLogger(__name__)


class test_partner(SharedSetupTransactionCase):

    _module_ns = 'ficep_membership'

    def setUp(self):
        super(test_partner, self).setUp()
        self.partner_obj = self.registry('res.partner')

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

        #create = without_membership
        partner = self.get_partner()
        self.assertEquals(partner.membership_state_id.code, 'without_membership', 'Create: should be "without_status"')

        #without_status -> candidate_member
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'candidate_member', 'Should be "candidate_member"')

        #without_status -> supporter
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': True})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'supporter', 'Should be "supporter"')

        #supporter -> candidate_member
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'candidate_member', 'Should be "candidate_member"')

        #candidate_member -> future_commitee_member
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'future_commitee_member', 'Should be "future_commitee_member"')

        #future_commitee_member -> refused_candidate_member
        partner.write({'rejected_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'refused_candidate_member', 'Should be "refused_candidate_member"')

        #refused candidate_member -> candidate_member
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'candidate_member', 'Should be "candidate_member"')

        #candidate_member ->supporter
        partner.write({'decline_payment_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': True})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'supporter', 'Should be "supporter"')

        #supporter -> old_supporter
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_supporter', 'Should be "old_supporter"')

        #go to member state
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'member', 'Should be "member"')

        # member -> old_member
        partner.write({'decline_payment_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_member', 'Should be "old member"')

        # old_member -> old_commitee_member
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
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
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        partner = self.get_partner(partner.id)

        # member -> resignation_old_member
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'resignation_old_member', 'Should be "resignation_old_member"')

        # Go to member
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        partner = self.get_partner(partner.id)

        # member -> expulsion_old_member
        partner.write({'exclusion_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'expulsion_old_member', 'Should be "expulsion_old_member"')

        # Go to old commitee member
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        partner = self.get_partner(partner.id)

        # member -> old_member
        partner.write({'decline_payment_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_member', 'Should be "old member"')

        # old_member -> old_commitee_member
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'old_commitee_member', 'Should be "old_commitee_member"')

        #old_commitee_member -> break_old_member
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)

        # go to old member
        partner = self.get_partner()
        partner.write({'accepted_date': date.today().strftime('%Y-%m-%d'),
                       'free_member': False})
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        wf_service.trg_validate(uid, 'res.partner', partner.id, 'free_pass', self.cr)
        partner = self.get_partner(partner.id)

        # member -> old_member
        partner.write({'resignation_date': date.today().strftime('%Y-%m-%d')})
        partner = self.get_partner(partner.id)
        self.assertEquals(partner.membership_state_id.code, 'break_old_member', 'Should be "break_old_member"')

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
        #check each tume the current state cs
        return self.partner_obj.browse(self.cr, self.uid, partner_id)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
