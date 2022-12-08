# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class MembershipRequest(models.Model):
    _inherit = "membership.request"

    force_autoval = fields.Boolean(
        string="Auto-validation will be forced",
        default=False,
        compute="_compute_force_autoval",
        store=True,
    )

    def _compute_force_autoval(self):
        """
        Intended to be extended for event, petition and survey.
        """
        for record in self:
            record.force_autoval = record.force_autoval

    @api.model
    def _find_lastname(self, vals):
        """
        Check if a lastname is given.
        It can be given
        * in vals, OR
        * by partner_id in vals

        (Intended to be extended for special AMA cases)
        """
        return vals.get("lastname", False) or vals.get("partner_id", False)

    def _create_membership_request(self, vals):
        #  If 'zip' is given in vals (as coming from an event for example),
        #  add it also in zip_man
        if "zip" in vals and "zip_man" not in vals:
            vals["zip_man"] = vals["zip"]
        if self._find_lastname(vals):
            request = self.with_context(mode="pre_process").create(vals)
            return request

    def _auto_validate_may_be_forced(self, auto_validate):
        self.ensure_one()
        failure_reason = self._auto_validate(auto_validate)

        if failure_reason:
            self._create_note(
                _("Autovalidation failed"),
                _("Autovalidation failed. Reason of failure: %s") % failure_reason,
            )

            if self.force_autoval:
                self.validate_request()
                if self.state == "validate":
                    self._create_note(
                        _("Forcing autovalidation"), _("Autovalidation was forced")
                    )
                else:
                    self._create_note(
                        _("Forcing autovalidation: attempt failed"),
                        _("Attempt to force auto-validation, but fail."),
                    )
