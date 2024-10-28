# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class MozaikDocumentFolder(models.Model):

    _name = "mozaik.document.folder"
    _description = "Folder for Mozaik Documents"
    _parent_store = True
    _oder = "name"

    name = fields.Char(required=True)
    parent_id = fields.Many2one(
        "mozaik.document.folder", ondelete="cascade", index=True
    )
    child_ids = fields.One2many(
        "mozaik.document.folder", "parent_id", string="Child Tags"
    )
    parent_path = fields.Char(index=True)

    def name_get(self):
        """
        Return the folders' display name, including their direct
        parent by default
        """
        res = []
        for folder in self:
            names = []
            current = folder
            while current:
                names.append(current.name)
                current = current.parent_id
            res.append((folder.id, " / ".join(reversed(names))))
        return res

    @api.model
    def _name_search(
        self, name, args=None, operator="ilike", limit=100, name_get_uid=None
    ):
        args = args or []
        if name:
            # Be sure name_search is symmetric to name_get
            name = name.split(" / ")[-1]
            args = [("name", operator, name)] + args
        return self._search(args, limit=limit, access_rights_uid=name_get_uid)
