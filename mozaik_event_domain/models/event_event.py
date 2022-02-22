# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models

DEFAULT_DOMAIN = "[]"


class EventEvent(models.Model):

    _inherit = "event.event"

    domain = fields.Text(
        string="Target partners domain",
        help="Add a domain on partners model to limit the access of this event.",
        default=DEFAULT_DOMAIN,
    )
    domain_is_set = fields.Boolean(
        string="Domain is set", compute="_compute_domain_is_set"
    )

    @api.depends("domain")
    def _compute_domain_is_set(self):
        for record in self:
            record.domain_is_set = record.domain != DEFAULT_DOMAIN
