# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from typing import List

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest_pydantic.restapi import PydanticModel, PydanticModelList
from odoo.addons.component.core import Component

from ..pydantic_models.survey_info import SurveyInfo, SurveyShortInfo
from ..pydantic_models.survey_search_filter import SurveySearchFilter


class SurveyService(Component):
    _inherit = "base.survey.rest.service"
    _name = "survey.rest.service"
    _usage = "survey"
    _expose_model = "survey.survey"
    _description = __doc__

    @restapi.method(
        routes=[(["/<int:_id>"], "GET")],
        output_param=PydanticModel(SurveyInfo),
        auth="public",
    )
    def get(self, _id: int) -> SurveyInfo:
        survey = self._get(_id)
        return SurveyInfo.from_orm(survey)

    def _get_search_domain(self, filters):
        domain = []
        if filters.title:
            domain.append(("title", "ilike", filters.title))
        if filters.id:
            domain.append(("id", "=", filters.id))
        if filters.is_private:
            domain.append(("is_private", "=", filters.is_private))
            if filters.int_instance_id:
                # Filtering on instance iff is_private=True
                domain.append(("int_instance_id", "=", filters.int_instance_id))
        if filters.publish_date_before:
            domain.append(("publish_date", "<", filters.publish_date_before))
        if filters.publish_date_after:
            domain.append(("publish_date", ">", filters.publish_date_after))
        if filters.interest_ids:
            domain.append(("interest_ids", "in", filters.interest_ids))
        return domain

    @restapi.method(
        routes=[(["/", "/search"], "GET")],
        input_param=PydanticModel(SurveySearchFilter),
        output_param=PydanticModelList(SurveyShortInfo),
        auth="public",
    )
    def search(self, survey_search_filter: SurveySearchFilter) -> List[SurveyShortInfo]:
        domain = self._get_search_domain(survey_search_filter)
        res: List[SurveyShortInfo] = []
        for e in self.env[self._expose_model].sudo().search(domain):
            res.append(SurveyShortInfo.from_orm(e))
        return res
