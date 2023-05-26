# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models


class PartnerInvolvement(models.Model):

    _inherit = "partner.involvement"

    include_in_summary = fields.Boolean(default=True, tracking=True)

    def _notes_to_summary(self):
        self.ensure_one()
        res = ""
        notes = []
        if self.note:
            notes.append(self.note)
        if self.involvement_category_id.note:
            notes.append(self.involvement_category_id.note)
        if notes:
            notes = [n.replace("\n", "//") for n in notes]
            res = ": %s" % " - ".join(notes)
        return res

    @api.model
    def create(self, vals):
        if "include_in_summary" not in vals and vals.get("involvement_category_id"):
            ic = self.env["partner.involvement.category"].browse(
                [vals["involvement_category_id"]]
            )
            vals["include_in_summary"] = ic.include_in_summary
        involvement = super().create(vals)
        if involvement.active and involvement.include_in_summary:
            change = _("New involvement %(name)s%(note)s") % {
                "name": involvement.display_name,
                "note": involvement._notes_to_summary(),
            }
            involvement.partner_id._add_change_to_partner(change, 130)
        return involvement

    @api.onchange("involvement_category_id")
    def _onchange_involvement_category_id(self):
        self.include_in_summary = self.involvement_category_id.include_in_summary
