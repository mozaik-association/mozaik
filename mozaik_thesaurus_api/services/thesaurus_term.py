# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.thesaurus_term_info import ThesaurusTermInfo
from ..pydantic_models.thesaurus_term_search_filter import ThesaurusTermSearchFilter


class ThesaurusTermService(Component):
    _inherit = "base.thesaurus.rest.service"
    _name = "thesaurus.term.rest.service"
    _usage = "thesaurus_term"
    _expose_model = "thesaurus.term"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(ThesaurusTermInfo),
    )
    def get(self, _id: int) -> ThesaurusTermInfo:
        thesaurus_term = self._get(_id)
        return ThesaurusTermInfo.from_orm(thesaurus_term)

    def _get_search_domain(self, filters):
        domain = []
        if filters.name:
            domain.append(("name", "like", filters.name))
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.active is not None:
            domain.append(("active", "=", filters.active))
        else:
            domain.extend(["|", ("active", "=", True), ("active", "=", False)])
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(ThesaurusTermSearchFilter),
        output_param=PydanticModelList(ThesaurusTermInfo),
    )
    def search(
        self, thesaurus_term_search_filter: ThesaurusTermSearchFilter
    ) -> List[ThesaurusTermInfo]:
        domain = self._get_search_domain(thesaurus_term_search_filter)
        res: List[ThesaurusTermInfo] = []
        for e in self.env["thesaurus.term"].sudo().search(domain):
            res.append(ThesaurusTermInfo.from_orm(e))
        return res
