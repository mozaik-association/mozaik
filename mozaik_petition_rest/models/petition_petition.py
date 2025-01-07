# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.http import request


class PetitionPetition(models.Model):

    _inherit = ["petition.petition"]

    image_url = fields.Char(string="Image URL", compute="_compute_image_url")
    is_headline = fields.Boolean(string="Headline")

    @api.depends("image")
    def _compute_image_url(self):
        host_url = request.httprequest.host_url
        for petition in self:
            petition.image_url = "%sweb/image_api/petition.petition/%d/image" % (
                host_url,
                petition.id,
            )
