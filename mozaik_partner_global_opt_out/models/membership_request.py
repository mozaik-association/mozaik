# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class MembershipRequest(models.Model):

    _inherit = "membership.request"

    force_global_opt_out = fields.Boolean(
        string="Force global opt-out",
        help="If ticked, set the field 'Global opt-out' to True on the partner.",
        default=False,
    )

    force_global_opt_in = fields.Boolean(
        string="Force global opt-in",
        help="If ticked, set the field 'Global opt-out' to False on the partner.",
        default=False,
    )

    @api.constrains("force_global_opt_out", "force_global_opt_in")
    def _check_force_global_opt_out(self):
        """
        Cannot tick simultaneously both
        force_global_opt_out
        and
        force_global_opt_in
        """
        for mr in self:
            if mr.force_global_opt_in and mr.force_global_opt_out:
                raise ValidationError(
                    _(
                        "Cannot tick simultaneously both 'global opt-out' and 'global opt-in'"
                    )
                )

    def validate_request(self):
        res = super().validate_request()
        for mr in self:
            partner = mr.partner_id
            if mr.force_global_opt_out and not partner.global_opt_out:
                partner.write({"global_opt_out": True})
            if mr.force_global_opt_in and partner.global_opt_out:
                mr.partner_id.write({"global_opt_out": False})
        return res
