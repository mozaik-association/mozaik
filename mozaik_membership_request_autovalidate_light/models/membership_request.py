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
            ("draft",),
            ("confirm",),
            ("validate",),
            ("light_autoval", "Treated via light auto-validation"),
            ("cancel",),
        ]
    )

    def write(self, vals):
        """
        Invalidate membership requests that were treated by light autovalidation
        """
        res = super().write(vals)
        if "state" in vals and vals["state"] == "light_autoval":
            self.action_invalidate()
        return res

    def _check_light_autoval(self, auto_val):
        self.ensure_one()
        failure_reason = ""
        if not auto_val:
            failure_reason = _("Auto validation manually set to false")
        # TODO: add checks for deciding if auto-val should be accepted or not
        return auto_val, failure_reason

    def _light_validate_request(self):
        self.ensure_one()
        # TODO: copy some fields on a new MR, validate it,
        #  set the first MR into light_autoval state
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
        auto_val, failure_reason = self._check_light_autoval(auto_val)
        if auto_val:
            # automatic light validation
            self._light_validate_request()

        return failure_reason
