# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestCronUpdateMembershipState(SavepointCase):
    """
    Tests for MembershipRequest.cron_update_membership_state().

    The cron must refresh ``membership_state_id`` (the partner's *current*
    state stored on the request) for every pending (draft / confirm) request
    that has a partner linked, without touching ``result_type_id``.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.mrs = cls.env["membership.state"]
        cls.mro = cls.env["membership.request"]
        cls.without_membership_state = cls.mrs.search(
            [("code", "=", "without_membership")]
        )
        cls.member_state = cls.mrs.search([("code", "=", "member")])
        cls.supporter_state = cls.mrs.search([("code", "=", "supporter")])
        # A plain partner (no membership → without_membership by default)
        cls.partner = cls.env["res.partner"].create(
            {
                "lastname": "Doe",
                "firstname": "John",
            }
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _create_draft_mr(self, partner, membership_state=None):
        """Create a draft membership request linked to *partner*."""
        mr = self.mro.create(
            {
                "lastname": partner.lastname,
                "firstname": partner.firstname,
                "partner_id": partner.id,
                "request_type": "m",
            }
        )
        if membership_state is not None:
            # Force a stale value to simulate a request created in the past
            mr.write({"membership_state_id": membership_state.id})
        return mr

    def _force_partner_state(self, partner, state):
        """Directly write the membership state on the partner (test shortcut)."""
        partner.write({"membership_state_id": state.id})

    # ------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------

    def test_cron_updates_stale_draft_request(self):
        """
        A draft request whose stored current state no longer matches the
        partner's actual state must be updated by the cron.
        """
        # Simulate: request was created when partner had no membership,
        # but the partner became a member in the meantime.
        mr = self._create_draft_mr(self.partner, self.without_membership_state)
        self._force_partner_state(self.partner, self.member_state)
        self.assertNotEqual(mr.membership_state_id, self.member_state)
        self.mro.cron_update_membership_state()
        self.assertEqual(
            mr.membership_state_id,
            self.member_state,
            "The cron should have refreshed membership_state_id to match the partner.",
        )

    def test_cron_updates_stale_confirmed_request(self):
        """
        A *confirmed* (state='confirm') request is also in scope for the cron.
        """
        mr = self._create_draft_mr(self.partner, self.without_membership_state)
        mr.confirm_request()
        self.assertEqual(mr.state, "confirm")
        self._force_partner_state(self.partner, self.supporter_state)
        self.mro.cron_update_membership_state()
        self.assertEqual(mr.membership_state_id, self.supporter_state)

    def test_cron_does_not_touch_validated_request(self):
        """
        Validated requests (state='validate') must be ignored by the cron.
        """
        mr = self._create_draft_mr(self.partner, self.without_membership_state)
        # Manually force to 'validate' without going through the full workflow
        mr.write({"state": "validate"})
        self._force_partner_state(self.partner, self.member_state)
        self.mro.cron_update_membership_state()
        self.assertEqual(
            mr.membership_state_id,
            self.without_membership_state,
            "Validated requests must not be touched by the cron.",
        )

    def test_cron_does_not_touch_cancelled_request(self):
        """
        Cancelled requests (state='cancel') must be ignored by the cron.
        """
        mr = self._create_draft_mr(self.partner, self.without_membership_state)
        mr.write({"state": "cancel"})
        self._force_partner_state(self.partner, self.member_state)
        self.mro.cron_update_membership_state()
        self.assertEqual(
            mr.membership_state_id,
            self.without_membership_state,
            "Cancelled requests must not be touched by the cron.",
        )

    def test_cron_does_not_touch_requests_without_partner(self):
        """
        Draft requests with no partner linked are out of scope: the cron
        must leave them untouched.
        """
        mr = self.mro.create(
            {
                "lastname": "Anonymous",
                "request_type": "m",
                # no partner_id
            }
        )
        original_state_id = mr.membership_state_id.id
        self.mro.cron_update_membership_state()
        self.assertEqual(
            mr.membership_state_id.id,
            original_state_id,
            "Requests without a partner must be skipped.",
        )

    def test_cron_updates_result_type_id_when_partner_state_changes(self):
        """
        Scenario:

        1. Partner is a member → request created with current=member, result=member
           (request_type=False, is_update request).
        2. Partner resigns → partner state becomes former_member.
        3. Cron runs → both membership_state_id AND result_type_id must be
           refreshed so that validating the request no longer re-opens a membership.
        """
        former_member_state = self.mrs.search([("code", "=", "former_member")])
        self.assertIsNotNone(former_member_state)
        # Step 1 – partner is member, DA is created
        self._force_partner_state(self.partner, self.member_state)
        mr = self._create_draft_mr(self.partner, self.member_state)
        mr.write({"result_type_id": self.member_state.id})
        # Step 2 – partner resigns
        self._force_partner_state(self.partner, former_member_state)
        # Step 3 – cron runs
        self.mro.cron_update_membership_state()
        self.assertEqual(
            mr.membership_state_id,
            former_member_state,
            "membership_state_id must reflect the partner's new state.",
        )
        # result_type_id must also have been refreshed (not stay on 'member')
        self.assertNotEqual(
            mr.result_type_id,
            self.member_state,
            "result_type_id must be recalculated so validation does not "
            "reopen a closed membership.",
        )
