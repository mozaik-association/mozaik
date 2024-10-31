# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _
from odoo.exceptions import MissingError

from odoo.addons.component.core import AbstractComponent


class BaseDocumentService(AbstractComponent):
    _inherit = "base.rest.service"
    _name = "base.document.service"
    _collection = "document.rest.services"
    _expose_model = None

    def _get(self, _id):
        domain = [("id", "=", _id)]
        record = self.env[self._expose_model].search(domain)
        if not record:
            raise MissingError(
                _("The record %(model)s %(id)s does not exist")
                % {"model": self._expose_model, "id": _id}
            )
        return record
