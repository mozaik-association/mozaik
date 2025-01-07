# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from typing import List

from odoo import _
from odoo.exceptions import ValidationError

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.all_documents_allowed_input import AllDocumentsAllowedInput
from ..pydantic_models.document_info import DocumentInfo, DocumentWithContentInfo


class DocumentService(Component):
    _inherit = "base.document.service"
    _name = "document.rest.service"
    _usage = "document"
    _expose_model = "mozaik.document"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(DocumentWithContentInfo),
    )
    def get(self, _id: int) -> DocumentWithContentInfo:
        document = self._get(_id)
        return DocumentWithContentInfo.from_orm(document)

    def _get_all_allowed_documents_for_partner(
        self, partner_id: int
    ) -> List[DocumentInfo]:
        if not partner_id:
            raise ValidationError(_("No partner is given."))
        all_documents = self.env["mozaik.document"].search([])
        allowed_documents = all_documents._filter_allowed_for_partner(partner_id)
        return [DocumentInfo.from_orm(document) for document in allowed_documents]

    @restapi.method(
        routes=[(["/get_all_allowed_documents"], "GET")],
        input_param=PydanticModel(AllDocumentsAllowedInput),
        output_param=PydanticModelList(DocumentInfo),
    )
    def get_all_allowed_documents(
        self,
        input_info: AllDocumentsAllowedInput,
    ) -> List[DocumentInfo]:
        partner_id = input_info.partner_id
        return self._get_all_allowed_documents_for_partner(partner_id)
