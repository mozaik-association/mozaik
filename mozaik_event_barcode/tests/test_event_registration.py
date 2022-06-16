# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests.common import TransactionCase


class TestEventRegistration(TransactionCase):
    def setUp(self):
        super().setUp()
        self.event_test = self.env["event.event"].create(
            {
                "name": "Test Event",
                "date_begin": fields.Datetime.now() - relativedelta(hours=4),
                "date_end": fields.Datetime.now() + relativedelta(days=3),
                "voting_domain": "[['partner_id.firstname', '=', 'Jean']]",
            }
        )
        self.partner_jean = self.env["res.partner"].create(
            {
                "lastname": "Dupont",
                "firstname": "Jean",
                "email": "j.d@test.com",
            }
        )
        self.partner_marc = self.env["res.partner"].create(
            {
                "lastname": "Lavoine",
                "firstname": "Marc",
                "email": "m.l@test.com",
            }
        )
        # Add a membership.line to the partners
        self.member_state = self.browse_ref("mozaik_membership.member")
        int_structure_05 = self.browse_ref("mozaik_structure.int_instance_05")
        wizard = self.env["add.membership"].create(
            {
                "partner_id": self.partner_jean.id,
                "int_instance_id": int_structure_05.id,
                "state_id": self.member_state.id,
                "date_from": fields.Date.today(),
            }
        )
        wizard.action_add()
        wizard = self.env["add.membership"].create(
            {
                "partner_id": self.partner_marc.id,
                "int_instance_id": int_structure_05.id,
                "state_id": self.member_state.id,
                "date_from": fields.Date.today(),
            }
        )
        wizard.action_add()
        # Register the partners
        self.reg_jean = self.env["event.registration"].create(
            {
                "associated_partner_id": self.partner_jean.id,
                "event_id": self.event_test.id,
            }
        )
        self.reg_marc = self.env["event.registration"].create(
            {
                "associated_partner_id": self.partner_marc.id,
                "event_id": self.event_test.id,
            }
        )

    def test_jean_is_member(self):
        """
        Check that Jean and Marc are members, to be able to work with.
        """
        self.assertEqual(self.partner_jean.membership_state_id.id, self.member_state.id)
        self.assertEqual(self.partner_marc.membership_state_id.id, self.member_state.id)

    def test_create_new_registration(self):
        """
        Registration with a partner that can vote
        -> check that can_vote is True
        Registration with a partner that cannot vote
        -> check that can_vote is False
        """
        self.assertTrue(self.reg_jean.can_vote)
        self.assertFalse(self.reg_marc.can_vote)

    def test_change_partner_info(self):
        """
        1. Change Jean's firstname -> can vote does not change
        2. Trigger recompute -> jean cannot vote anymore
        """
        self.partner_jean.write({"firstname": "JEAN"})
        self.assertTrue(self.reg_jean.can_vote)
        self.event_test.trigger_recompute_voting_domain()
        self.assertFalse(self.reg_jean.can_vote)

    def test_change_voting_domain(self):
        """
        Change voting domain -> Recompute must be triggered
        """
        self.event_test.write(
            {
                "voting_domain": "[['partner_id.firstname', '=', 'JEAN']]",
            }
        )
        self.assertFalse(self.reg_jean.can_vote)
