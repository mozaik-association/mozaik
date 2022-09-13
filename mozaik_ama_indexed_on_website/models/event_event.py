# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventEvent(models.Model):

    _inherit = "event.event"

    not_indexed_on_website = fields.Boolean(
        string="Not indexed on website", help="Only accessible by url"
    )
