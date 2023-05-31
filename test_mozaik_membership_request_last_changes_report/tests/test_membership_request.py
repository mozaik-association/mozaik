# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import SavepointCase


class TestMembershipRequest(SavepointCase):
    def setUp(self):
        super().setUp()

        # Activate all the change types
        system_param_keys = [
            "changes_report.log_instance_join",
            "changes_report.log_instance_left",
            "changes_report.log_supporter",
            "changes_report.log_member_committee",
            "changes_report.log_renewal",
            "changes_report.log_member",
            "changes_report.log_former_member_committee",
            "changes_report.log_former_member",
            "changes_report.log_former_supporter",
            "changes_report.log_break_former_member",
            "changes_report.log_expulsion_former_member",
            "changes_report.log_inappropriate_former_member",
            "changes_report.log_resignation_former_member",
            "changes_report.log_voluntaries_changes",
            "changes_report.log_email_changes",
            "changes_report.log_postal_changes",
            "changes_report.log_global_opt_out_changes",
        ]
        for key in system_param_keys:
            self.env["ir.config_parameter"].sudo().set_param(key, "True")

        self.harry = self.env["res.partner"].create(
            {"lastname": "Potter", "firstname": "Harry"}
        )
        self.supporter = self.env.ref("mozaik_membership.supporter")
        regional_power = self.env["int.power.level"].create({"name": "Regional"})
        self.int_lg = self.env["int.instance"].create(
            {
                "name": "Liège",
                "power_level_id": regional_power.id,
            }
        )
        self.int_bxl = self.env["int.instance"].create(
            {
                "name": "Bruxelles",
                "power_level_id": regional_power.id,
            }
        )
        self.lg = self.env["res.city"].create(
            {
                "name": "Liège",
                "zipcode": 4000,
                "country_id": self.env.ref("base.be").id,
                "int_instance_id": self.int_lg.id,
            }
        )
        self.bxl = self.env["res.city"].create(
            {
                "name": "Bruxelles",
                "zipcode": 1000,
                "country_id": self.env.ref("base.be").id,
                "int_instance_id": self.int_bxl.id,
            }
        )
        self.address_lg = self.env["address.address"].create(
            {
                "street_man": "Rue du puits",
                "number": 12,
                "city_id": self.lg.id,
            }
        )

    def test_membership_request_change_address_last_changes(self):
        """
        Partner is supporter and has a complete address.
        Create a new MR and change the address (with an instance change) on it.
        -> Check changes:
        * On the old ML: 'Thanks to note the new address' + 'Has left your instance'
        * On the new ML: 'Has joined your instance'
        """
        self.env["add.membership"].create(
            {
                "partner_id": self.harry.id,
                "state_id": self.supporter.id,
                "int_instance_id": self.int_lg.id,
                "date_from": fields.Date.today() - relativedelta(days=1),
            }
        ).action_add()
        self.assertEqual(self.harry.membership_state_id.code, "supporter")
        self.env["change.address"].create(
            {
                "address_id": self.address_lg.id,
                "partner_ids": [self.harry.id],
            }
        ).doit()
        self.harry.membership_line_ids.reset_last_changes()
        self.assertEqual(self.harry.int_instance_ids.ids, [self.int_lg.id])
        self.harry.button_modification_request()
        mr = self.env["membership.request"].search([("partner_id", "=", self.harry.id)])
        self.assertEqual(len(mr), 1)
        mr.city_id = self.bxl
        mr.onchange_city_id()
        self.assertEqual(mr.int_instance_ids.ids, [self.int_bxl.id])
        mr.confirm_request()
        mr.validate_request()
        old_ml = self.harry.membership_line_ids.filtered(lambda ml: not ml.active)
        new_ml = self.harry.membership_line_ids.filtered("active")
        self.assertEqual(len(old_ml), 1)
        self.assertEqual(len(new_ml), 1)
        old_changes = old_ml.last_changes or ""
        new_changes = new_ml.last_changes or ""
        self.assertEqual(
            len(old_changes.split("\n")), 2
        )  # New address + left your instance
        self.assertEqual(len(new_changes.split("\n")), 1)  # Joined your instance
        self.assertTrue("510" in old_changes and "520" in old_changes)
        self.assertTrue("100" in new_changes)

    def test_creating_supporter_and_involvement(self):
        """
        A partner is without membership.
        Create a membership request to make him become a supporter and
        involve into a category that must be logged
        -> Check that 2 changes were logged on the membership line.
        """
        partner = self.env["res.partner"].create(
            {"lastname": "Potter", "firstname": "Harry"}
        )
        ic = self.env["partner.involvement.category"].create(
            {"name": "Logged IC", "include_in_summary": True}
        )
        mr = self.env["membership.request"].create(
            {
                "partner_id": partner.id,
                "lastname": partner.lastname,
                "request_type": "s",
                "involvement_category_ids": [(4, ic.id)],
            }
        )
        mr.write(
            mr._onchange_partner_id_vals(
                mr.is_company, mr.request_type, partner.id, mr.technical_name
            )
        )
        mr.confirm_request()
        mr.validate_request()
        ml = partner.membership_line_ids
        self.assertEqual(len(ml), 1)
        changes = ml.last_changes.split("\n")
        self.assertEqual(len(changes), 2)
