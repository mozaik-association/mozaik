# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo import fields

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.involvement import Involvement
from ..pydantic_models.involvement_info import InvolvementInfo
from ..pydantic_models.involvement_search_filter import InvolvementSearchFilter


class InvolvementService(Component):
    _inherit = "base.partner.involvement.category.rest.service"
    _name = "partner.involvement.rest.service"
    _usage = "involvement"
    _expose_model = "partner.involvement"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(InvolvementInfo),
    )
    def get(self, _id: int) -> InvolvementInfo:
        involvement = self._get(_id)
        return InvolvementInfo.from_orm(involvement)

    def _get_search_domain(self, filters):
        domain = []
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.partner_id:
            domain.append(("partner_id", "=", filters.id))
        if filters.partner_name:
            domain.append(("partner_id.name", "ilike", filters.partner_name))
        if filters.category_name:
            domain.append(
                ("involvement_category_id.name", "ilike", filters.category_name)
            )
        if filters.category_code:
            domain.append(
                ("involvement_category_id.code", "ilike", filters.category_code)
            )
        if filters.involvement_type:
            domain.append(("involvement_type", "=", filters.involvement_type))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(InvolvementSearchFilter),
        output_param=PydanticModelList(InvolvementInfo),
    )
    def search(
        self, involvement_search_filter: InvolvementSearchFilter
    ) -> List[InvolvementInfo]:
        domain = self._get_search_domain(involvement_search_filter)
        res: List[InvolvementInfo] = []
        for inv in self.env["partner.involvement"].sudo().search(domain):
            res.append(InvolvementInfo.from_orm(inv))
        return res

    def _prep_involvement_values(self, input_data):
        vals = input_data.dict()
        if not vals.get("effective_time"):
            vals["effective_time"] = fields.Datetime.now()
        return vals

    def _create_involvement(self, involvement):
        vals = self._prep_involvement_values(involvement)
        return self.env["partner.involvement"].create(vals)

    @restapi.method(
        routes=[(["/involvement"], "POST")],
        input_param=PydanticModel(Involvement),
        output_param=PydanticModel(InvolvementInfo),
    )
    def involvement(self, involvement: Involvement) -> InvolvementInfo:
        inv = self._create_involvement(involvement)
        return InvolvementInfo.from_orm(inv)
