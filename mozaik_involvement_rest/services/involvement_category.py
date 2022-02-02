# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.involvement_category_info import InvolvementCategoryInfo
from ..pydantic_models.involvement_category_search_filter import (
    InvolvementCategorySearchFilter,
)


class InvolvementCategoryService(Component):
    _inherit = "base.partner.involvement.category.rest.service"
    _name = "partner.involvement.category.rest.service"
    _usage = "involvement_category"
    _expose_model = "partner.involvement.category"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(InvolvementCategoryInfo),
        auth="public",
    )
    def get(self, _id: int) -> InvolvementCategoryInfo:
        involvement_category = self._get(_id)
        return InvolvementCategoryInfo.from_orm(involvement_category)

    def _get_search_domain(self, filters):
        domain = []
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.code:
            domain.append(("code", "like", filters.code))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(InvolvementCategorySearchFilter),
        output_param=PydanticModelList(InvolvementCategoryInfo),
        auth="public",
    )
    def search(
        self, involvement_category_search_filter: InvolvementCategorySearchFilter
    ) -> List[InvolvementCategoryInfo]:
        domain = self._get_search_domain(involvement_category_search_filter)
        res: List[InvolvementCategoryInfo] = []
        for ic in self.env["partner.involvement.category"].sudo().search(domain):
            res.append(InvolvementCategoryInfo.from_orm(ic))
        return res
