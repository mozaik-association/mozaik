# Copyright 2026 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, fields, models


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    autovalidation_type = fields.Selection(
        [("light", "Light"), ("complete", "Complete")], default="complete"
    )
    state = fields.Selection(
        selection_add=[
            ("light_autoval", "Treated via light auto-validation"),
            ("cancel",),
        ]
    )
    light_mr_id = fields.Many2one(
        "membership.request",
        string="Light Membership Request",
        help="Associated light auto-validated membership request linked to this MR.",
    )
    complete_mr_id = fields.Many2one(
        "membership.request",
        string="Complete Membership Request",
        help="Membership request that lead to the generation of this light MR.",
    )

    def action_invalidate(self, vals=None):
        """
        Don't invalidate other MR in cascade, otherwise Max Depth Recursion Error
        between light MR and complete MR.
        """
        return super(
            MembershipRequest,
            self.with_context(invalidate_keep_active_models="membership.request"),
        ).action_invalidate(vals)

    def write(self, vals):
        """
        Invalidate membership requests that were treated by light autovalidation
        """
        res = super().write(vals)
        if "state" in vals and vals["state"] == "light_autoval":
            self.action_invalidate()
        return res

    def _check_light_autoval(self, auto_val):
        """
        Returns a dict containing the following parameters
        * auto_val is True if auto_validation is permitted, False otherwise
        * failure reason is the reason why auto_validation is not permitted (empty if auto_val
        is True)
        * partner is the matched partner, if found. Else False

        See ticket #88373 for light auto-validation details.
        """
        self.ensure_one()
        res = {
            "auto_val": auto_val,
            "failure_reason": "",
            "partner": False,
        }
        if not res["auto_val"]:
            res["failure_reason"] = _("Auto validation manually set to false")
            return res
        if not self.email:
            res.update(
                {
                    "auto_val": False,
                    "failure_reason": _("Email is required for light autovalidation."),
                }
            )
            return res
        matched_partners = self.env["res.partner"].search(
            [("email", "=", self.email)], limit=2
        )
        if len(matched_partners) > 1:
            res.update(
                {
                    "auto_val": False,
                    "failure_reason": _(
                        "Several partners found with email '%s'. Light autovalidation failed."
                        % self.email
                    ),
                }
            )
            return res
        if len(matched_partners) == 1:
            res["partner"] = matched_partners
        return res

    def _has_full_address(self):
        """
        Return True if one of the fields street/number/... is filled
        """
        self.ensure_one()
        return (
            self.address_local_street_id
            or self.street_man
            or self.street2
            or self.number
            or self.box
            or self.sequence
        )

    def _prepare_address_vals_for_light_mr(self, matched_partner):
        """
        Rules for copying address from the MR to the light MR are the following:
        - Matched partner & only city and/or zip on MR & no address on matched partner
          -> copy city and/or zip
        - No matched partner: copy full address from MR
        - Other cases: don't copy any address field.

        """
        self.ensure_one()
        if (
            matched_partner
            and not matched_partner.address_address_id
            and not self._has_full_address()
        ):
            return {
                "country_id": self.country_id.id,
                "zip_man": self.zip_man,
                "city_man": self.city_man,
                "city_id": self.city_id.id,
            }
        if not matched_partner:
            return {
                "country_id": self.country_id.id,
                "zip_man": self.zip_man,
                "city_man": self.city_man,
                "city_id": self.city_id.id,
                "address_local_street_id": self.address_local_street_id.id,
                "street_man": self.street_man,
                "street2": self.street2,
                "number": self.number,
                "box": self.box,
                "sequence": self.sequence,
            }
        return {}

    def _prepare_vals_for_light_mr(self, matched_partner):
        """
        Copy part of the values of self to create the light MR.
        """
        # TODO. Check if commands must be better copied
        #  + Check if all dependencies are included.
        self.ensure_one()
        vals = {}
        if matched_partner:
            vals.update(
                {
                    "lastname": matched_partner.lastname,
                    "firstname": matched_partner.firstname,
                    "partner_id": matched_partner.id,
                }
            )
        else:
            vals.update(
                {
                    "lastname": self.lastname,
                    "firstname": self.firstname,
                }
            )
        vals.update(
            {
                "email": self.email,
                # Involvements
                "effective_time": self.effective_time,
                "involvement_category_ids": self.involvement_category_ids,
                # Thesaurus
                "competency_ids": self.competency_ids,
                "interest_ids": self.interest_ids,
                "indexation_comments": self.indexation_comments,
                # Payment
                "amount": self.amount,  # TODO: other payment fields
            }
        )
        vals.update(self._prepare_address_vals_for_light_mr(matched_partner))

        return vals

    def _light_validate_request(self, matched_partner):
        self.ensure_one()
        # Create light MR
        create_vals = self._prepare_vals_for_light_mr(matched_partner)
        light_mr = self.env["membership.request"].create(create_vals)
        # Link both MR
        light_mr.complete_mr_id = self
        self.light_mr_id = light_mr
        # Validate light MR
        light_mr.validate_request()
        if light_mr.state == "validate":
            self.write({"state": "light_autoval"})

    def _auto_validate(self, auto_val=True):
        """
        Call the super() auto-validation for complete auto-validation only.
        """
        self.ensure_one()
        if not self.autovalidation_type:
            return _(
                "No autovalidation (neither complete or partial) selected on the MR."
            )
        if self.autovalidation_type == "complete":
            return super()._auto_validate(auto_val)
        # Light auto-validation
        light_autoval_res = self._check_light_autoval(auto_val)
        if light_autoval_res["auto_val"]:
            # automatic light validation
            self._light_validate_request(matched_partner=light_autoval_res["partner"])

        return light_autoval_res["failure_reason"]
