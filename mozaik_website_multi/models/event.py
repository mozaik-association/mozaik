# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class Event(models.Model):

    _inherit = "event.event"

    website_domain_ids = fields.Many2many(
        comodel_name="website.domain", string="Website Domains"
    )
