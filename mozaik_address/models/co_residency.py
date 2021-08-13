# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models, fields, _


class CoResidency(models.Model):

    _name = "co.residency"
    _inherit = ["mozaik.abstract.model"]
    _description = "Co-Residency"
    _rec_name = "address_id"

    _unicity_keys = "address_id"
    _inactive_cascade = True

    address_id = fields.Many2one(
        "address.address",
        string="Address",
        required=True,
        readonly=True,
        index=True,
    )
    line = fields.Char("Line 1", track_visibility="onchange")
    line2 = fields.Char("Line 2", track_visibility="onchange")

    postal_coordinate_ids = fields.One2many(
        "postal.coordinate", "co_residency_id", string="Postal Coordinates"
    )

    def name_get(self):
        """
        :rparam: list of (id, name)
                 where id is the id of each object
                 and name, the name to display.
        :rtype: [(id, name)] list of tuple
        """
        res = []
        for record in self:
            if not record.line and not record.line2:
                name = _("Co-Residency to complete")
            else:
                name = "/".join(
                    [line for line in [record.line, record.line2] if line]
                )
            res.append((record["id"], name))
        return res

    def unlink(self):
        """
        Force "undo allow duplicate" when deleting a co-residency
        """
        cids = self.env["postal.coordinate"]
        for c in self:
            cids += c.postal_coordinate_ids
        if cids:
            cids.button_undo_allow_duplicate()
        res = super().unlink()
        return res
