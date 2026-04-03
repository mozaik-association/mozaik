# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests.common import SavepointCase


class TestMailingTrace(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestMailingTrace, cls).setUpClass()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Partner",
                "email": "test@example.com",
            }
        )
        cls.mailing = cls.env["mailing.mailing"].create(
            {
                "subject": "Test Mailing",
                "body_html": "<p>Test</p>",
                "mailing_model_id": cls.env["ir.model"]._get("res.partner").id,
            }
        )

    def _create_mailing_trace(self, **kwargs):
        """Helper to create a mailing.trace record linked to a partner."""
        defaults = {
            "model": "res.partner",
            "res_id": self.partner.id,
            "mass_mailing_id": self.mailing.id,
        }
        defaults.update(kwargs)
        return self.env["mailing.trace"].create(defaults)


class TestMailingTracePartnerCompute(TestMailingTrace):
    def test_compute_partner_id_with_partner_model(self):
        """
        When model is 'res.partner' and res_id is a valid partner,
        partner_id should be set to that partner.
        """
        trace = self._create_mailing_trace()
        self.assertEqual(trace.partner_id, self.partner)

    def test_compute_partner_id_with_non_partner_model(self):
        """
        When model is not 'res.partner',
        partner_id should remain empty.
        """
        other_model = "mailing.contact"
        mailing_contact = self.env["mailing.contact"].create(
            {"name": "Test Contact", "email": "contact@example.com"}
        )
        mailing_for_contact = self.env["mailing.mailing"].create(
            {
                "subject": "Test Mailing Contact",
                "body_html": "<p>Test</p>",
                "mailing_model_id": self.env["ir.model"]._get(other_model).id,
            }
        )
        trace = self.env["mailing.trace"].create(
            {
                "model": other_model,
                "res_id": mailing_contact.id,
                "mass_mailing_id": mailing_for_contact.id,
            }
        )
        self.assertFalse(trace.partner_id)

    def test_compute_partner_id_with_invalid_res_id(self):
        """
        When res_id does not correspond to an existing partner,
        partner_id should remain empty.
        """
        trace = self._create_mailing_trace(res_id=999999999)
        self.assertFalse(trace.partner_id)

    def test_compute_partner_id_with_no_model(self):
        """
        When model is not set, partner_id should remain empty.
        """
        trace = self.env["mailing.trace"].create(
            {
                "model": "res.partner",
                "res_id": self.partner.id,
                "mass_mailing_id": self.mailing.id,
            }
        )
        trace.write({"model": False})
        trace.invalidate_cache(["partner_id"])
        trace._compute_partner_id()
        self.assertFalse(trace.partner_id)


class TestMailingTraceStatusCompute(TestMailingTrace):
    def test_is_received_true_when_sent_without_exception(self):
        """
        is_received should be True when sent is set and exception is not.
        """
        trace = self._create_mailing_trace(sent=datetime.now(), exception=False)
        self.assertTrue(trace.is_received)

    def test_is_received_false_when_not_sent(self):
        """
        is_received should be False when sent is not set.
        """
        trace = self._create_mailing_trace(sent=False, exception=False)
        self.assertFalse(trace.is_received)

    def test_is_received_false_when_exception(self):
        """
        is_received should be False when there is an exception,
        even if sent is set.
        """
        trace = self._create_mailing_trace(
            sent=datetime.now(), exception=datetime.now()
        )
        self.assertFalse(trace.is_received)

    def test_is_opened_true_when_opened(self):
        """
        is_opened should be True when opened is set.
        """
        trace = self._create_mailing_trace(opened=datetime.now())
        self.assertTrue(trace.is_opened)

    def test_is_opened_false_when_not_opened(self):
        """
        is_opened should be False when opened is not set.
        """
        trace = self._create_mailing_trace(opened=False)
        self.assertFalse(trace.is_opened)

    def test_is_clicked_true_when_clicked(self):
        """
        is_clicked should be True when clicked is set.
        """
        trace = self._create_mailing_trace(clicked=datetime.now())
        self.assertTrue(trace.is_clicked)

    def test_is_clicked_false_when_not_clicked(self):
        """
        is_clicked should be False when clicked is not set.
        """
        trace = self._create_mailing_trace(clicked=False)
        self.assertFalse(trace.is_clicked)

    def test_full_engagement_trace(self):
        """
        A fully engaged trace should have all statuses set to True.
        """
        now = datetime.now()
        trace = self._create_mailing_trace(
            sent=now,
            exception=False,
            opened=now,
            clicked=now,
        )
        self.assertTrue(trace.is_received)
        self.assertTrue(trace.is_opened)
        self.assertTrue(trace.is_clicked)


class TestResPartnerMailingTrace(TestMailingTrace):
    def test_mailing_trace_count_no_traces(self):
        """
        A partner with no mailing traces should have a count of 0.
        """
        self.assertEqual(self.partner.mailing_trace_count, 0)

    def test_mailing_trace_count_single_trace(self):
        """
        A partner with one mailing trace should have a count of 1.
        """
        self._create_mailing_trace()
        self.assertEqual(self.partner.mailing_trace_count, 1)

    def test_mailing_trace_count_multiple_traces(self):
        """
        A partner with multiple mailing traces should
        have the correct count.
        """
        self._create_mailing_trace()
        self._create_mailing_trace()
        self._create_mailing_trace()
        self.assertEqual(self.partner.mailing_trace_count, 3)

    def test_mailing_trace_count_only_counts_own_traces(self):
        """
        A partner's mailing trace count should not include
        traces linked to other partners.
        """
        other_partner = self.env["res.partner"].create(
            {
                "name": "Other Partner",
                "email": "other@example.com",
            }
        )
        self._create_mailing_trace()
        self._create_mailing_trace(res_id=other_partner.id)
        self.assertEqual(self.partner.mailing_trace_count, 1)
        self.assertEqual(other_partner.mailing_trace_count, 1)

    def test_action_view_mailing_traces_type(self):
        """
        action_view_mailing_traces should return an act_window action.
        """
        action = self.partner.action_view_mailing_traces()
        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "mailing.trace")

    def test_action_view_mailing_traces_domain(self):
        """
        The returned action domain should filter by the partner's id.
        """
        action = self.partner.action_view_mailing_traces()
        self.assertIn(("partner_id", "=", self.partner.id), action["domain"])

    def test_action_view_mailing_traces_context(self):
        """
        The returned action context should contain the default and
        search default for partner_id.
        """
        action = self.partner.action_view_mailing_traces()
        self.assertEqual(action["context"]["default_partner_id"], self.partner.id)
        self.assertEqual(
            action["context"]["search_default_partner_id"], self.partner.id
        )

    def test_action_view_mailing_traces_view_mode(self):
        """
        The returned action should use tree and form view modes.
        """
        action = self.partner.action_view_mailing_traces()
        self.assertEqual(action["view_mode"], "tree,form")

    def test_action_view_mailing_traces_tree_view(self):
        """
        The returned action should reference the custom tree view
        from the module.
        """
        action = self.partner.action_view_mailing_traces()
        expected_view_id = self.env.ref(
            "mozaik_mass_mailing_partner.mailing_trace_partner_tree_view"
        ).id
        tree_view = next((v for v in action["views"] if v[1] == "tree"), None)
        self.assertIsNotNone(tree_view)
        self.assertEqual(tree_view[0], expected_view_id)
