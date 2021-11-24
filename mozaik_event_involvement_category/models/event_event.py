# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class EventType(models.Model):

    _inherit = "event.type"

    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category", string="Involvement Category"
    )


class EventEvent(models.Model):

    _inherit = "event.event"

    involvement_category_id = fields.Many2one(
        comodel_name="partner.involvement.category",
        string="Involvement Category",
        compute="_compute_involvement_category_id",
        store=True,
        readonly=False,
    )

    @api.depends("event_type_id")
    def _compute_involvement_category_id(self):
        """Update event configuration from its event type. Depends are set only
        on event_type_id itself, not its sub fields. Purpose is to emulate an
        onchange: if event type is changed, update event configuration. Changing
        event type content itself should not trigger this method."""
        for event in self:
            if event.event_type_id and event.event_type_id.involvement_category_id:
                event.involvement_category_id = (
                    event.event_type_id.involvement_category_id
                )
            else:
                event.involvement_category_id = False
