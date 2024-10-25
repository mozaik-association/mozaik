# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class MozaikDocument(models.Model):

    _name = "mozaik.document"
    _description = "Mozaik Document"
    _inherit = ["mozaik.privacy.domain.mixin"]

    name = fields.Char(required=True)
    folder_id = fields.Many2one(
        "mozaik.document.folder", required=True, ondelete="restrict"
    )
    content = fields.Binary()
    content_filename = fields.Char()
    url = fields.Char()

    active = fields.Boolean(default=True)
