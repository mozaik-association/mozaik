# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class WebsiteDomain(models.Model):

    _name = "website.domain"
    _description = "Website Domain"

    name = fields.Char(required=True)
