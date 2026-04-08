# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestMembershipRequestInvolvement(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

        cls.involvement_category = cls.env["partner.involvement.category"].create(
            {
                "name": "Test Involvement Category",
                "involvement_type": "voluntary",
                "allow_multi": False,
            }
        )
        cls.involvement_category_multi = cls.env["partner.involvement.category"].create(
            {
                "name": "Test Multi Category",
                "involvement_type": "voluntary",
                "allow_multi": True,
            }
        )
        cls.partner = cls.env["res.partner"].create(
            {
                "lastname": "Test Partner",
            }
        )

    def _create_membership_request(self, involvement_lines=None, **kwargs):
        """Helper to create a membership request with involvement lines."""
        vals = {
            "lastname": self.partner.lastname,
        }
        vals.update(kwargs)
        if involvement_lines:
            vals["membership_request_involvement_ids"] = [
                (0, 0, line) for line in involvement_lines
            ]
        return self.env["membership.request"].create(vals)

    def _validate_membership_request(self, mr):
        """Helper to go through the full workflow: draft -> confirm -> validate."""
        mr.partner_id = self.partner
        mr.confirm_request()
        mr.validate_request()

    def test_involvement_note_propagated_on_validate(self):
        """
        Test that when a membership request is validated, the note
        from the intermediate model is propagated to the partner.involvement.
        """
        note_text = "This is a test note for the involvement"
        mr = self._create_membership_request(
            involvement_lines=[
                {
                    "involvement_category_id": self.involvement_category.id,
                    "note": note_text,
                },
            ],
        )
        # Ensure the line was created
        self.assertEqual(len(mr.membership_request_involvement_ids), 1)
        self.assertEqual(
            mr.membership_request_involvement_ids.note,
            note_text,
        )
        # Also check the computed many2many
        self.assertIn(self.involvement_category, mr.involvement_category_ids)

        # Validate the membership request through the full workflow
        self._validate_membership_request(mr)

        # Check that the involvement was created with the note
        involvement = self.env["partner.involvement"].search(
            [
                ("partner_id", "=", self.partner.id),
                ("involvement_category_id", "=", self.involvement_category.id),
            ]
        )
        self.assertEqual(len(involvement), 1)
        self.assertEqual(involvement.note, note_text)

    def test_involvement_without_note(self):
        """
        Test that involvement creation still works when no note is provided.
        """
        mr = self._create_membership_request(
            involvement_lines=[
                {
                    "involvement_category_id": self.involvement_category.id,
                },
            ],
        )

        self._validate_membership_request(mr)

        involvement = self.env["partner.involvement"].search(
            [
                ("partner_id", "=", self.partner.id),
                ("involvement_category_id", "=", self.involvement_category.id),
            ]
        )
        self.assertEqual(len(involvement), 1)
        self.assertFalse(involvement.note)

    def test_backward_compat_involvement_category_ids(self):
        """
        Test that setting involvement_category_ids (Many2many) still works
        through the inverse method, for backward compatibility.
        """
        mr = self._create_membership_request()
        mr.involvement_category_ids = [
            (6, 0, [self.involvement_category.id, self.involvement_category_multi.id])
        ]
        self.assertEqual(len(mr.membership_request_involvement_ids), 2)
        categories = mr.membership_request_involvement_ids.mapped(
            "involvement_category_id"
        )
        self.assertIn(self.involvement_category, categories)
        self.assertIn(self.involvement_category_multi, categories)

    def test_multiple_involvements_different_notes(self):
        """
        Test that different notes can be set for different involvement categories.
        """
        note1 = "Note for category 1"
        note2 = "Note for category 2"
        mr = self._create_membership_request(
            involvement_lines=[
                {
                    "involvement_category_id": self.involvement_category.id,
                    "note": note1,
                },
                {
                    "involvement_category_id": self.involvement_category_multi.id,
                    "note": note2,
                },
            ],
        )
        self.assertEqual(len(mr.membership_request_involvement_ids), 2)

        self._validate_membership_request(mr)

        inv1 = self.env["partner.involvement"].search(
            [
                ("partner_id", "=", self.partner.id),
                ("involvement_category_id", "=", self.involvement_category.id),
            ]
        )
        inv2 = self.env["partner.involvement"].search(
            [
                ("partner_id", "=", self.partner.id),
                (
                    "involvement_category_id",
                    "=",
                    self.involvement_category_multi.id,
                ),
            ]
        )
        self.assertEqual(inv1.note, note1)
        self.assertEqual(inv2.note, note2)

    def test_computed_involvement_category_ids(self):
        """
        Test that the computed involvement_category_ids field returns
        the correct categories from the intermediate model.
        """
        mr = self._create_membership_request(
            involvement_lines=[
                {
                    "involvement_category_id": self.involvement_category.id,
                    "note": "some note",
                },
            ],
        )
        self.assertEqual(
            mr.involvement_category_ids,
            self.involvement_category,
        )
