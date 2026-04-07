# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestMembershipRequestInvolvementREST(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.ic1 = cls.env["partner.involvement.category"].create(
            {
                "name": "REST Cat 1",
                "involvement_type": "voluntary",
                "allow_multi": False,
                "code": "REST_CAT_1",
            }
        )
        cls.ic2 = cls.env["partner.involvement.category"].create(
            {
                "name": "REST Cat 2",
                "involvement_type": "voluntary",
                "allow_multi": True,
                "code": "REST_CAT_2",
            }
        )

    def _validate_involvement_category(self, vals):
        """Call _validate_involvement_category from the service class directly.

        Since the service is a Component and not an Odoo model, we import
        the class and call the method with self.env as context.
        """
        from ..services.membership_request import MembershipRequestService

        class _FakeService:
            pass

        svc = _FakeService()
        svc.env = self.env
        return MembershipRequestService._validate_involvement_category(svc, vals)

    # ── tests on _validate_involvement_category ──────────────────────────

    def test_new_format_with_notes(self):
        """'involvements' creates intermediate lines with notes."""
        vals = {
            "involvements": [
                {"involvement_category_id": self.ic1.id, "note": "Note 1"},
                {"involvement_category_id": self.ic2.id, "note": "Note 2"},
            ],
            "involvement_category_ids": [],
            "involvement_category_codes": [],
        }
        vals = self._validate_involvement_category(vals)
        lines = vals.get("membership_request_involvement_ids", [])
        self.assertEqual(len(lines), 2)

        line_vals = [line[2] for line in lines]
        cat_ids = [v["involvement_category_id"] for v in line_vals]
        self.assertIn(self.ic1.id, cat_ids)
        self.assertIn(self.ic2.id, cat_ids)

        by_cat = {v["involvement_category_id"]: v for v in line_vals}
        self.assertEqual(by_cat[self.ic1.id]["note"], "Note 1")
        self.assertEqual(by_cat[self.ic2.id]["note"], "Note 2")

        self.assertNotIn("involvement_category_ids", vals)
        self.assertNotIn("involvement_category_codes", vals)
        self.assertNotIn("involvements", vals)

    def test_new_format_without_notes(self):
        """'involvements' without notes still creates lines."""
        vals = {
            "involvements": [
                {"involvement_category_id": self.ic1.id},
            ],
            "involvement_category_ids": [],
            "involvement_category_codes": [],
        }
        vals = self._validate_involvement_category(vals)
        lines = vals.get("membership_request_involvement_ids", [])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0][2]["involvement_category_id"], self.ic1.id)
        self.assertNotIn("note", lines[0][2])

    def test_new_format_with_code(self):
        """'involvements' can use involvement_category_code."""
        vals = {
            "involvements": [
                {"involvement_category_code": "REST_CAT_1", "note": "By code"},
            ],
            "involvement_category_ids": [],
            "involvement_category_codes": [],
        }
        vals = self._validate_involvement_category(vals)
        lines = vals.get("membership_request_involvement_ids", [])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0][2]["involvement_category_id"], self.ic1.id)
        self.assertEqual(lines[0][2]["note"], "By code")

    def test_deprecated_format_ids(self):
        """Old 'involvement_category_ids' still works (no notes)."""
        vals = {
            "involvements": [],
            "involvement_category_ids": [self.ic1.id, self.ic2.id],
            "involvement_category_codes": [],
        }
        vals = self._validate_involvement_category(vals)
        lines = vals.get("membership_request_involvement_ids", [])
        self.assertEqual(len(lines), 2)
        cat_ids = {line[2]["involvement_category_id"] for line in lines}
        self.assertEqual(cat_ids, {self.ic1.id, self.ic2.id})
        for line in lines:
            self.assertNotIn("note", line[2])

    def test_deprecated_format_codes(self):
        """Old 'involvement_category_codes' still works (no notes)."""
        vals = {
            "involvements": [],
            "involvement_category_ids": [],
            "involvement_category_codes": ["REST_CAT_1", "REST_CAT_2"],
        }
        vals = self._validate_involvement_category(vals)
        lines = vals.get("membership_request_involvement_ids", [])
        self.assertEqual(len(lines), 2)

    def test_new_format_takes_precedence(self):
        """When both formats are given, 'involvements' wins."""
        vals = {
            "involvements": [
                {"involvement_category_id": self.ic1.id, "note": "Wins"},
            ],
            "involvement_category_ids": [self.ic2.id],
            "involvement_category_codes": [],
        }
        vals = self._validate_involvement_category(vals)
        lines = vals.get("membership_request_involvement_ids", [])
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0][2]["involvement_category_id"], self.ic1.id)
        self.assertEqual(lines[0][2]["note"], "Wins")

    # ── end-to-end ORM tests ────────────────────────────────────────────

    def test_end_to_end_create_with_notes(self):
        """Create a membership.request directly with the new format
        and verify the intermediate lines are created correctly."""
        mr = self.env["membership.request"].create(
            {
                "lastname": "REST Test",
                "firstname": "Partner",
                "request_type": "m",
                "membership_request_involvement_ids": [
                    (
                        0,
                        0,
                        {
                            "involvement_category_id": self.ic1.id,
                            "note": "E2E note",
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "involvement_category_id": self.ic2.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(len(mr.membership_request_involvement_ids), 2)
        line1 = mr.membership_request_involvement_ids.filtered(
            lambda rec: rec.involvement_category_id == self.ic1
        )
        line2 = mr.membership_request_involvement_ids.filtered(
            lambda rec: rec.involvement_category_id == self.ic2
        )
        self.assertEqual(line1.note, "E2E note")
        self.assertFalse(line2.note)
