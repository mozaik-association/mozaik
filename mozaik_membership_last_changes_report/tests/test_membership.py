# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import datetime

from odoo import fields
from odoo.tests import SavepointCase


class TestMembership(SavepointCase):
    def get_lines(self, membership_line):
        membership_line.ensure_one()
        changes = (
            membership_line.last_changes.split("\n")
            if membership_line.last_changes
            else []
        )
        return [c[5:] for c in sorted(changes)]

    def test_notifications(self):
        """
        Check for last changes reported to locale instance
        """
        # get a partner
        partner = self.browse_ref("mozaik_address.res_partner_jacques")
        self.assertFalse(partner.membership_line_ids)

        # change its instance
        vals = {
            "partner_ids": partner.ids,
            "instance_id": self.ref("mozaik_structure.int_instance_01"),
        }
        wz = self.env["change.instance"].create(vals)
        wz.doit()
        self.assertFalse(partner.membership_line_ids)

        # create a membership line
        state = self.env.ref("mozaik_membership.member")
        w = self.env["add.membership"].create(
            {
                "int_instance_id": partner.int_instance_id.id,
                "partner_id": partner.id,
                "product_id": partner.subscription_product_id.id,
                "state_id": state.id,
                "price": 10,
                "date_from": fields.Date.today() - datetime.timedelta(days=1),
            }
        )
        w.action_add()
        self.assertTrue(partner.membership_line_ids)

        ml1 = partner.membership_line_ids[0]
        self.assertEqual(
            ml1.last_changes,
            "210: Status has been changed: False → Member. "
            "The person becomes a member in full",
        )
        nbl = 1

        # add an involvement
        ic = self.env["partner.involvement.category"].create(
            {
                "name": "Organisation Euro 2020",
                "include_in_summary": True,
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        self.env["partner.involvement"].create(
            {
                "partner_id": partner.id,
                "involvement_category_id": ic.id,
            }
        )
        nbl += 1
        self.assertEqual(len(ml1.last_changes.split("\n")), nbl)

        # add an involvement (not logged)

        ic = self.env["partner.involvement.category"].create(
            vals={
                "name": "Organisation Euro 2024",
                "res_users_ids": [(4, self.env.ref("base.user_admin").id)],
            }
        )
        self.env["partner.involvement"].create(
            {
                "partner_id": partner.id,
                "involvement_category_id": ic.id,
            }
        )
        nbl += 0
        self.assertEqual(len(ml1.last_changes.split("\n")), nbl)

        # change its address and its internal instance
        vals = {
            "address_id": self.ref("mozaik_address.address_1"),
            "partner_ids": partner.ids,
            "update_instance": True,
        }
        wz = self.env["change.address"].create(vals)
        wz.doit()
        nbl += 2
        self.assertEqual(len(ml1.last_changes.split("\n")), nbl)
        nbs = nbl

        ml2 = partner.membership_line_ids[-1]
        self.assertNotEqual(ml1, ml2)
        nbl = 1
        self.assertEqual(len(ml2.last_changes.split("\n")), nbl)

        # paid, accept and renew subscription
        ml2.write({"paid": True})
        state = self.env.ref("mozaik_membership.member")
        w = self.env["add.membership"].create(
            {
                "int_instance_id": partner.int_instance_id.id,
                "partner_id": partner.id,
                "date_from": fields.Date.to_string(
                    ml2.date_from.replace(year=ml2.date_from.year + 1)
                ),
                "product_id": partner.subscription_product_id.id,
                "state_id": state.id,
                "price": 10,
            }
        )
        w.action_add()
        nbl += 1
        self.assertEqual(len(ml2.last_changes.split("\n")), nbl)
        ml = partner.membership_line_ids[-1]
        self.assertFalse(ml.last_changes)

        # Change some voluntaries
        partner.write(
            {
                "regional_voluntary": True,
            }
        )
        self.assertEqual(1, len(self.get_lines(ml)))

        # last changes of ml1 remains untouched
        self.assertEqual(len(self.get_lines(ml1)), nbs)
        self.assertEqual("130", min(x[0:3] for x in ml1.last_changes.split("\n")))
        self.assertEqual(130, ml1.last_changes_sequence)  # i.e. min() of all changes

        # count messages to secretariats
        self.env["membership.line"].send_last_changes()

        # all last_changes must be empty now
        last_changes = self.env["membership.line"].get_last_changes()
        self.assertFalse(last_changes)

    def test_notifications_several_instances(self):
        """
        A partner has membership lines on different instances.
        When changing the membership state (without changing the instance),
        he must not have change lines indicating that
        his instance changed (this test asserts that the bug was fixed)
        """
        harry = self.env["res.partner"].create({"name": "Harry Potter"})
        instance_01_id = self.ref("mozaik_structure.int_instance_01")
        instance_02_id = self.ref("mozaik_structure.int_instance_02")
        member_id = self.ref("mozaik_membership.member")
        former_member_id = self.ref("mozaik_membership.former_member")
        self.env["add.membership"].create(
            {
                "int_instance_id": instance_01_id,
                "partner_id": harry.id,
                "state_id": member_id,
                "price": 10,
                "date_from": fields.Date.today() - datetime.timedelta(days=1),
            }
        ).action_add()
        self.assertEqual(harry.int_instance_id.id, instance_01_id)
        self.assertEqual(harry.membership_state_code, "member")

        # Change instance
        self.env["change.instance"].create(
            {"instance_id": instance_02_id, "partner_ids": [(4, harry.id)]}
        ).doit()
        self.assertEqual(harry.int_instance_id.id, instance_02_id)

        # Change membership state (new membership line): only one change
        self.env["add.membership"].create(
            {
                "int_instance_id": instance_02_id,
                "partner_id": harry.id,
                "state_id": former_member_id,
                "date_from": fields.Date.today(),
            }
        ).action_add()
        self.assertEqual(harry.int_instance_id.id, instance_02_id)
        self.assertEqual(harry.membership_state_code, "former_member")
        active_ml = harry.membership_line_ids.filtered("active")
        self.assertFalse(active_ml.last_changes)

    def test_creating_supporter_and_involvement(self):
        """
        A partner is without membership.
        Make him become a supporter so he has a membership line.
        Create him a partner involvement that must be included in the summary
        and check that it is the case.
        """
        partner = self.env["res.partner"].create(
            {"lastname": "Potter", "firstname": "Harry"}
        )
        instance_01_id = self.ref("mozaik_structure.int_instance_01")
        supporter_id = self.ref("mozaik_membership.supporter")
        self.env["add.membership"].create(
            {
                "int_instance_id": instance_01_id,
                "partner_id": partner.id,
                "state_id": supporter_id,
                "date_from": fields.Date.today(),
            }
        ).action_add()
        ic = self.env["partner.involvement.category"].create(
            {"name": "Logged IC", "include_in_summary": True}
        )
        ml = partner.membership_line_ids
        self.assertEqual(len(ml), 1)
        changes = ml.last_changes.split("\n")
        self.assertEqual(len(changes), 1)
        partner.partner_involvement_ids = [(0, 0, {"involvement_category_id": ic.id})]
        changes = ml.last_changes.split("\n")
        self.assertEqual(len(changes), 2)
