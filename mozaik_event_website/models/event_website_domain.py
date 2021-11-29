# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class EventWebsiteDomain(models.Model):

    _name = "event.website.domain"
    _description = "Event Website Domain"

    name = fields.Char(required=True)
