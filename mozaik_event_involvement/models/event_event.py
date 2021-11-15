# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    auto_accept_membership = fields.Boolean(
        string="Accept membership requests",
        help="Membership requests that can be linked to a "
        "unique existing partner are automatically accepted.",
        default=True,
    )

    @api.model
    def create(self, vals):
        """
        When creating a new event, it triggers the creation of a new involvement category,
        whose name is the event name and which is linked to this event.
        Each attendee to the event will have involvements of this involvement category.
        """
        rec = super().create(vals)
        values = {
            "name": rec.name,
            "allow_multi": True,
            "involvement_type": "event",
            "event_id": rec.id,
        }
        self.env["partner.involvement.category"].create(values)

        return rec
