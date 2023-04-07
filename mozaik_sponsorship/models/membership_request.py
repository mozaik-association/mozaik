# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    can_be_sponsored = fields.Boolean(compute="_compute_can_be_sponsored")
    sponsor_id = fields.Many2one("res.partner")

    @api.constrains("sponsor_id", "partner_id")
    def check_parent_different_from_self(self):
        for mr in self:
            if mr.sponsor_id and mr.sponsor_id == mr.partner_id:
                raise ValidationError(_("A partner cannot be sponsored by itself"))

    @api.depends("partner_id", "partner_id.membership_state_id")
    def _compute_can_be_sponsored(self):
        """
        Partner can NOT be sponsored if:
        * he's a member or (former) member committee
        * he's a former member (or former member break,...) and already has a sponsor

        He can be sponsored in all other cases (including if he's a new contact)
        """
        self.can_be_sponsored = True
        for mr in self.filtered("partner_id"):
            partner = mr.partner_id
            if partner.membership_state_id.code in [
                "member",
                "member_committee",
                "former_member_committee",
            ]:
                mr.can_be_sponsored = False
            elif (
                partner.membership_state_id.code
                in [
                    "former_member",
                    "expulsion_former_member",
                    "resignation_former_member",
                    "inappropriate_former_member",
                    "break_former_member",
                ]
                and partner.sponsor_id
            ):
                mr.can_be_sponsored = False

    def validate_request(self):
        """
        Write the sponsor on the partner
        """
        # Must check can_be_sponsored boolean before validation, otherwise
        # the membership state of the partner change.
        mr_can_be_sponsored = self.filtered("can_be_sponsored")

        res = super().validate_request()

        for mr in mr_can_be_sponsored.filtered(
            lambda mr: mr.partner_id and mr.sponsor_id
        ):
            mr.partner_id.sponsor_id = mr.sponsor_id
        return res

    def _validate_request_membership(self, partner):  # noqa: C901
        """
        When validating the MR, if the partner already has an active membership line
        in the same state as the MR result state, we do not create a new membership
        line, but we update the existing one (update price, product and reference).

        The problem is that we update the price only if it is > 0
        (We cannot update a price = 0 otherwise every MR will modify existing
        membership lines, even if they don't intend to do it, as 0 is the default value).
        But sponsored memberships are likely to involve free membership products.

        Hence, in the special sponsorship context (if sponsor_id is filled on the MR),
        we allow to modify the price and the product. We search for the corresponding
        product based on membership tarification rules. We thus ignore the amount
        that could have been added on the membership request.
        """
        # Check which lines are already existing and for which we just have to change
        # the price. We must avoid to process new membership lines, otherwise
        # we will reset the price as the default price of the product, but the price
        # may have been changed on the MR
        active_memberships = partner.membership_line_ids.filtered("active")
        membership_lines_to_update = self.env["membership.line"].browse()
        for membership_instance in active_memberships:
            if (
                membership_instance
                and membership_instance.state_id == self.result_type_id
            ):
                membership_lines_to_update |= membership_instance

        res = super()._validate_request_membership(partner)

        if self.sponsor_id and self.result_type_id.code in (
            "member",
            "member_candidate",
        ):
            product = partner.with_context(
                membership_request_id=self.id
            ).subscription_product_id
            if product:
                instances = self.force_int_instance_id | self.int_instance_ids
                membership_instances = membership_lines_to_update.filtered(
                    lambda m: m.int_instance_id in instances and not m.paid
                )
                vals = {
                    "product_id": product.id,
                    "price": product.list_price,
                }
                if vals["price"] == 0:
                    vals["paid"] = True
                membership_instances.write(vals)

                # Post the changes
                for membership in membership_instances:
                    body = (
                        _("Membership changed with membership request:")
                        + "<br/><ul class='o_Message_trackingValues'>"
                    )
                    arrow = "<div class='fa fa-long-arrow-right'></div>"
                    body += _("<li>Price: %(previous)s %(arrow)s %(after)s</li>") % {
                        "previous": membership.price,
                        "arrow": arrow,
                        "after": product.price,
                    }
                    body += _("<li>Product: %(previous)s %(arrow)s %(after)s</li>") % {
                        "previous": membership.product_id.name,
                        "arrow": arrow,
                        "after": product.name,
                    }
                    membership.partner_id.message_post(body=body)

                    # Advance workflow for membership lines that became free
                    membership._advance_in_workflow()

        return res
