# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    def _auto_validate(self, auto_val):
        """
        Checks conditions from ticket #26993 to accept auto_validation
        or not. If accepted, then auto_validate.
        """
        self.ensure_one()

        # membership request without email
        if auto_val and not self.email:
            auto_val = False

        fields_tokeep_empty = [
            self.street_man,
            self.number,
            self.box,
            self.mobile,
            self.phone,
        ]
        nb_match_emails = 0

        # 26993/2.1.1 and 2.3.2 (first part)
        if auto_val and any(fields_tokeep_empty):
            auto_val = False

        # 26993/2.3.1
        if auto_val and self.partner_id:
            # for existing partner, state cannot be conflictual
            auto_val = self.partner_id.membership_state_code not in [
                "former_supporter",
                "refused_member_candidate",
                "expulsion_former_member",
                "resignation_former_member",
                "inappropriate_former_member",
                "break_former_member",
            ]

        # 26993/2.3.2 (second part)
        if auto_val and self.partner_id:
            # for existing partner, names must be equal
            auto_val = (
                self.partner_id.firstname == self.firstname
                and self.partner_id.lastname == self.lastname
            )

        # 26993/2.4.2.2.2 - first part
        if (
            auto_val
            and self.partner_id
            and self.address_id
            and self.partner_id.country_id
        ):
            # for existing partner with address, zip must be equal
            auto_val = self.partner_id.zip == self.address_id.zip

        # 26993/2.4.2.2.2 - second part
        if auto_val and self.partner_id and self.city_id and self.partner_id.country_id:
            # for existing partner with address, zip must be equal
            auto_val = self.partner_id.zip == self.city_id.zipcode

        if auto_val and self.email:
            # get the number of email in res.partner
            nb_match_emails = (
                self.env["res.partner"]
                .sudo()
                .with_context(active_test=False)
                .search_count([("email", "=", self.email)])
            )

        # 26993/2.2
        if auto_val and self.partner_id:
            # for new partner, email must be unknown
            auto_val = nb_match_emails <= 1

        # 26993/2.? - email exists but is not main
        if auto_val and not self.partner_id:
            # for new partner, email must be unknown
            auto_val = nb_match_emails == 0

        if auto_val:
            # automatic validation
            self.validate_request()
