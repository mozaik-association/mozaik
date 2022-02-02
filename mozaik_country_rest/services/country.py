# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.country_info import CountryInfo
from ..pydantic_models.country_search_filter import CountrySearchFilter


class CountryService(Component):
    _inherit = "base.country.rest.service"
    _name = "country.rest.service"
    _usage = "country"
    _expose_model = "res.country"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(CountryInfo),
        auth="public",
    )
    def get(self, _id: int) -> CountryInfo:
        country = self._get(_id)
        return CountryInfo.from_orm(country)

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
        input_param=PydanticModel(CountrySearchFilter),
        output_param=PydanticModelList(CountryInfo),
        auth="public",
    )
    def search(self, country_search_filter: CountrySearchFilter) -> List[CountryInfo]:
        domain = self._get_search_domain(country_search_filter)
        res: List[CountryInfo] = []
        for c in self.env["res.country"].sudo().search(domain):
            res.append(CountryInfo.from_orm(c))
        return res
