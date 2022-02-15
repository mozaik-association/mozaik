# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    def _check_auto_validation_with_emails(self, auto_val):
        nb_match_emails = 0
        failure_reason = ""
        if self.email:
            # get the number of email in res.partner
            nb_match_emails = (
                self.env["res.partner"]
                .sudo()
                .with_context(active_test=False)
                .search_count([("email", "=", self.email)])
            )

        # 26993/2.2
        if auto_val and self.partner_id:
            auto_val = nb_match_emails <= 1
            if not auto_val:
                failure_reason = _("Email used for more than one partner")

        # 26993/2.? - email exists but is not main
        elif auto_val and not self.partner_id:
            # for new partner, email must be unknown
            auto_val = nb_match_emails == 0
            if not auto_val:
                failure_reason = _("New partner but already known email")
        return auto_val, failure_reason

    def _auto_validate(self, auto_val):
        """
        Checks conditions from ticket #26993 to accept auto_validation
        or not. If accepted, then auto_validate.
        If not, returns the raison of refusing auto-validation.
        """
        self.ensure_one()
        failure_reason = ""
        if not auto_val:
            failure_reason = _("Auto validation manually set to false")
        # membership request without email
        if auto_val and not self.email:
            auto_val = False
            failure_reason = _("No email provided")

        fields_tokeep_empty = [
            self.street_man,
            self.number,
            self.box,
            self.mobile,
            self.phone,
        ]

        # 26993/2.1.1 and 2.3.2 (first part)
        if auto_val and any(fields_tokeep_empty):
            auto_val = False
            failure_reason = _(
                "One of the following fields "
                "is completed: street_man, number, box, mobile, phone"
            )

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
            if not auto_val:
                failure_reason = _("Partner membership state is conflictual")

        # 26993/2.3.2 (second part)
        if auto_val and self.partner_id:
            # for existing partner, names must be equal
            auto_val = (
                self.partner_id.firstname == self.firstname
                and self.partner_id.lastname == self.lastname
            )
            if not auto_val:
                failure_reason = _("Firstname and lastname do not correspond")

        # 26993/2.4.2.2.2 - first part
        if (
            auto_val
            and self.partner_id
            and self.address_id
            and self.partner_id.country_id
        ):
            # for existing partner with address, zip must be equal
            auto_val = self.partner_id.zip == self.address_id.zip
            if not auto_val:
                failure_reason = _(
                    "Zip on the partner and zip on the address do not correspond"
                )

        # 26993/2.4.2.2.2 - second part
        if auto_val and self.partner_id and self.city_id and self.partner_id.country_id:
            # for existing partner with address, zip must be equal
            auto_val = self.partner_id.zip == self.city_id.zipcode
            if not auto_val:
                failure_reason = _(
                    "Zip on the partner and zip on the city do not correspond"
                )

        if auto_val:
            auto_val, failure_reason = self._check_auto_validation_with_emails(auto_val)

        if auto_val:
            # automatic validation
            self.validate_request()

        return failure_reason

    def _create_note(self, subject, body):
        """
        Given a subject and a body, write a note in the chatter
        on the request.
        """
        self.ensure_one()
        self.write(
            {
                "message_ids": [
                    (
                        0,
                        0,
                        {
                            "subject": subject,
                            "body": body,
                            "message_type": "comment",
                            "model": "membership.request",
                            "res_id": self.id,
                        },
                    )
                ]
            }
        )
