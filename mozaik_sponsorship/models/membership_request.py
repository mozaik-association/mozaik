# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


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
        Write the sponsor on the partner and tick the is_sponsored_membership
        boolean on active ML linked to instances referenced in the MR
        """
        # Must check can_be_sponsored boolean before validation, otherwise
        # the membership state of the partner changes.
        mr_can_be_sponsored = self.filtered("can_be_sponsored")
        sponsored_mr = mr_can_be_sponsored.filtered("sponsor_id")
        if sponsored_mr:
            sponsorship_product = self.env["product.product"].search(
                [("is_sponsorship_product", "=", True)], limit=1
            )
            if not sponsorship_product:
                raise UserError(
                    _(
                        "Please configure a sponsorship product by ticking "
                        "'Is sponsorship subscription' checkbox"
                    )
                )
            sponsored_mr.write({"force_product_id": sponsorship_product.id})

        res = super().validate_request()

        for mr in mr_can_be_sponsored.filtered(
            lambda mr: mr.partner_id and mr.sponsor_id
        ):
            mr.partner_id.sponsor_id = mr.sponsor_id
            for instance in mr.force_int_instance_id or mr.int_instance_ids:
                membership_instance = mr.partner_id.membership_line_ids.filtered(
                    lambda ml, i=instance: ml.active and ml.int_instance_id == i
                )
                membership_instance.is_sponsored = True
        return res
