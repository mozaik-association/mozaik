# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, models, fields

FAILURE_AVAILABLE_TYPES = [
    ("returned2sender", "Returned to sender"),
    ("nomail", "No longer receives mail at the mentioned address"),
    ("moved", "Moved"),
    ("bad", "Incomplete/Invalid address"),
    ("unknown", "Unknown"),
    ("refused", "Refused"),
    ("deceased", "Deceased"),
    ("unclaimed", "Unclaimed"),
    ("improper", "Improper box number"),
]


class FailureEditor(models.TransientModel):

    _name = "failure.editor.address"
    _inherit = "failure.editor"

    reason = fields.Selection(FAILURE_AVAILABLE_TYPES, default=False)
    description = fields.Text(
        default=lambda s: _("Returned to sender"),
        required=True,
    )

    @api.onchange("reason")
    def onchange_reason(self):
        self.ensure_one()
        if not self.reason:
            return
        field = self.fields_get(["reason"])["reason"]
        for value_id, value_trs in field["selection"]:
            if value_id == self.reason:
                self.description = value_trs
                return
