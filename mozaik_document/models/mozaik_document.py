# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


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
    content_filesize = fields.Integer(compute="_compute_content_filesize")
    url = fields.Char()

    active = fields.Boolean(default=True)

    @api.depends("content")
    def _compute_content_filesize(self):
        attachments = (
            self.env["ir.attachment"]
            .sudo()
            .search(
                [
                    ("res_field", "=", "content"),
                    ("res_model", "=", "mozaik.document"),
                    ("res_id", "in", self.ids),
                ]
            )
        )
        file_size_by_doc_id = {
            attachment.res_id: attachment.file_size for attachment in attachments
        }
        for doc in self:
            doc.content_filesize = file_size_by_doc_id.get(doc.id, 0)
